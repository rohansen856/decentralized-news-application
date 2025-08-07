package handlers

import (
	"database/sql"

	"news-app-go/internal/auth"
	"news-app-go/internal/database"
	"news-app-go/internal/models"
	"news-app-go/pkg/response"
	"news-app-go/pkg/validation"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

type AuthHandler struct {
	db         *database.Manager
	jwtManager *auth.JWTManager
	validator  *validation.Validator
}

func NewAuthHandler(db *database.Manager, jwtManager *auth.JWTManager, validator *validation.Validator) *AuthHandler {
	return &AuthHandler{
		db:         db,
		jwtManager: jwtManager,
		validator:  validator,
	}
}

func (h *AuthHandler) Register(c *gin.Context) {
	var req models.UserCreate
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, "Invalid request body", map[string]interface{}{"error": err.Error()})
		return
	}

	if err := h.validator.Validate(&req); err != nil {
		errors := h.validator.FormatValidationErrors(err)
		response.ValidationError(c, errors)
		return
	}

	existingUser, err := h.getUserByEmail(req.Email)
	if err != nil && err != sql.ErrNoRows {
		response.InternalServerError(c, "Database error", map[string]interface{}{"error": err.Error()})
		return
	}
	if existingUser != nil {
		response.Conflict(c, "User with this email already exists", nil)
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		response.InternalServerError(c, "Failed to hash password", nil)
		return
	}

	userID := uuid.New()
	user := &models.User{
		ID:           userID,
		Username:     req.Username,
		Email:        req.Email,
		PasswordHash: string(hashedPassword),
		Role:         req.Role,
		AnonymousMode: req.AnonymousMode,
		ProfileData:   req.ProfileData,
		Preferences:   req.Preferences,
		IsActive:      true,
		VerificationStatus: false,
		ReputationScore:    0.0,
	}

	if user.Role == "" {
		user.Role = models.RoleReader
	}
	if user.ProfileData == nil {
		user.ProfileData = make(map[string]interface{})
	}
	if user.Preferences == nil {
		user.Preferences = make(map[string]interface{})
	}

	if err := h.createUser(user); err != nil {
		response.InternalServerError(c, "Failed to create user", map[string]interface{}{"error": err.Error()})
		return
	}

	token, err := h.jwtManager.GenerateToken(user)
	if err != nil {
		response.InternalServerError(c, "Failed to generate token", nil)
		return
	}

	tokenResponse := &models.TokenResponse{
		AccessToken: token,
		TokenType:   "bearer",
		ExpiresIn:   86400, // 24 hours in seconds
		User:        user.ToResponse(),
		BaseResponse: *models.NewSuccessResponse("User registered successfully"),
	}

	response.Created(c, tokenResponse, "User registered successfully")
}

func (h *AuthHandler) Login(c *gin.Context) {
	var req models.UserLogin
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, "Invalid request body", map[string]interface{}{"error": err.Error()})
		return
	}

	if err := h.validator.Validate(&req); err != nil {
		errors := h.validator.FormatValidationErrors(err)
		response.ValidationError(c, errors)
		return
	}

	user, err := h.getUserByEmail(req.Email)
	if err != nil {
		if err == sql.ErrNoRows {
			response.Unauthorized(c, "Invalid email or password")
		} else {
			response.InternalServerError(c, "Database error", map[string]interface{}{"error": err.Error()})
		}
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(req.Password)); err != nil {
		response.Unauthorized(c, "Invalid email or password")
		return
	}

	if !user.IsActive {
		response.Forbidden(c, "Account is deactivated")
		return
	}

	token, err := h.jwtManager.GenerateToken(user)
	if err != nil {
		response.InternalServerError(c, "Failed to generate token", nil)
		return
	}

	if err := h.updateLastActive(user.ID); err != nil {
		// Log but don't fail the login
	}

	tokenResponse := &models.TokenResponse{
		AccessToken: token,
		TokenType:   "bearer",
		ExpiresIn:   86400, // 24 hours in seconds
		User:        user.ToResponse(),
		BaseResponse: *models.NewSuccessResponse("Login successful"),
	}

	response.Success(c, tokenResponse, "Login successful")
}

func (h *AuthHandler) GetProfile(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		response.Unauthorized(c, "User ID not found in context")
		return
	}

	id, ok := userID.(uuid.UUID)
	if !ok {
		response.InternalServerError(c, "Invalid user ID format", nil)
		return
	}

	user, err := h.getUserByID(id)
	if err != nil {
		if err == sql.ErrNoRows {
			response.NotFound(c, "User not found")
		} else {
			response.InternalServerError(c, "Database error", map[string]interface{}{"error": err.Error()})
		}
		return
	}

	response.Success(c, user.ToResponse(), "Profile retrieved successfully")
}

func (h *AuthHandler) getUserByEmail(email string) (*models.User, error) {
	query := `
		SELECT id, username, email, password_hash, role, did_address, anonymous_mode,
			   profile_data, preferences, created_at, updated_at, last_active,
			   is_active, verification_status, reputation_score
		FROM users WHERE email = $1
	`
	
	user := &models.User{}
	var profileDataJSON, preferencesJSON []byte
	
	err := h.db.Postgres.GetDB().QueryRow(query, email).Scan(
		&user.ID, &user.Username, &user.Email, &user.PasswordHash, &user.Role,
		&user.DIDAddress, &user.AnonymousMode, &profileDataJSON, &preferencesJSON,
		&user.CreatedAt, &user.UpdatedAt, &user.LastActive, &user.IsActive,
		&user.VerificationStatus, &user.ReputationScore,
	)
	
	if err != nil {
		return nil, err
	}

	// Handle JSON data
	if len(profileDataJSON) > 0 {
		// Parse JSON data
	}
	if len(preferencesJSON) > 0 {
		// Parse JSON data
	}
	
	return user, nil
}

func (h *AuthHandler) getUserByID(id uuid.UUID) (*models.User, error) {
	query := `
		SELECT id, username, email, password_hash, role, did_address, anonymous_mode,
			   profile_data, preferences, created_at, updated_at, last_active,
			   is_active, verification_status, reputation_score
		FROM users WHERE id = $1
	`
	
	user := &models.User{}
	var profileDataJSON, preferencesJSON []byte
	
	err := h.db.Postgres.GetDB().QueryRow(query, id).Scan(
		&user.ID, &user.Username, &user.Email, &user.PasswordHash, &user.Role,
		&user.DIDAddress, &user.AnonymousMode, &profileDataJSON, &preferencesJSON,
		&user.CreatedAt, &user.UpdatedAt, &user.LastActive, &user.IsActive,
		&user.VerificationStatus, &user.ReputationScore,
	)
	
	return user, err
}

func (h *AuthHandler) createUser(user *models.User) error {
	query := `
		INSERT INTO users (id, username, email, password_hash, role, anonymous_mode,
						  profile_data, preferences, created_at, updated_at, last_active,
						  is_active, verification_status, reputation_score)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW(), NOW(), $9, $10, $11)
	`
	
	profileJSON, _ := h.db.Postgres.PrepareJSONData(user.ProfileData)
	preferencesJSON, _ := h.db.Postgres.PrepareJSONData(user.Preferences)
	
	_, err := h.db.Postgres.GetDB().Exec(query,
		user.ID, user.Username, user.Email, user.PasswordHash, user.Role,
		user.AnonymousMode, profileJSON, preferencesJSON, user.IsActive,
		user.VerificationStatus, user.ReputationScore,
	)
	
	return err
}

func (h *AuthHandler) updateLastActive(userID uuid.UUID) error {
	query := "UPDATE users SET last_active = NOW() WHERE id = $1"
	_, err := h.db.Postgres.GetDB().Exec(query, userID)
	return err
}