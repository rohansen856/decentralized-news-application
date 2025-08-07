package models

import (
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type UserRole string

const (
	RoleAuthor        UserRole = "author"
	RoleReader        UserRole = "reader"
	RoleAdministrator UserRole = "administrator"
	RoleAuditor       UserRole = "auditor"
)

type User struct {
	ID                 uuid.UUID              `json:"id" db:"id"`
	Username           string                 `json:"username" db:"username" validate:"required,min=3,max=50"`
	Email              string                 `json:"email" db:"email" validate:"required,email"`
	PasswordHash       string                 `json:"-" db:"password_hash"`
	Role               UserRole               `json:"role" db:"role"`
	DIDAddress         *string                `json:"did_address,omitempty" db:"did_address"`
	AnonymousMode      bool                   `json:"anonymous_mode" db:"anonymous_mode"`
	ProfileData        map[string]interface{} `json:"profile_data,omitempty" db:"profile_data"`
	Preferences        map[string]interface{} `json:"preferences,omitempty" db:"preferences"`
	CreatedAt          time.Time              `json:"created_at" db:"created_at"`
	UpdatedAt          time.Time              `json:"updated_at" db:"updated_at"`
	LastActive         time.Time              `json:"last_active" db:"last_active"`
	IsActive           bool                   `json:"is_active" db:"is_active"`
	VerificationStatus bool                   `json:"verification_status" db:"verification_status"`
	ReputationScore    float64                `json:"reputation_score" db:"reputation_score"`
}

type UserCreate struct {
	Username      string                 `json:"username" validate:"required,min=3,max=50"`
	Email         string                 `json:"email" validate:"required,email"`
	Password      string                 `json:"password" validate:"required,min=8"`
	Role          UserRole               `json:"role,omitempty"`
	AnonymousMode bool                   `json:"anonymous_mode,omitempty"`
	ProfileData   map[string]interface{} `json:"profile_data,omitempty"`
	Preferences   map[string]interface{} `json:"preferences,omitempty"`
}

type UserUpdate struct {
	Username      *string                `json:"username,omitempty" validate:"omitempty,min=3,max=50"`
	Email         *string                `json:"email,omitempty" validate:"omitempty,email"`
	Role          *UserRole              `json:"role,omitempty"`
	AnonymousMode *bool                  `json:"anonymous_mode,omitempty"`
	ProfileData   map[string]interface{} `json:"profile_data,omitempty"`
	Preferences   map[string]interface{} `json:"preferences,omitempty"`
}

type UserLogin struct {
	Email    string `json:"email" validate:"required,email"`
	Password string `json:"password" validate:"required"`
}

type UserResponse struct {
	ID                 uuid.UUID              `json:"id"`
	Username           string                 `json:"username"`
	Email              string                 `json:"email"`
	Role               UserRole               `json:"role"`
	DIDAddress         *string                `json:"did_address,omitempty"`
	AnonymousMode      bool                   `json:"anonymous_mode"`
	ProfileData        map[string]interface{} `json:"profile_data,omitempty"`
	Preferences        map[string]interface{} `json:"preferences,omitempty"`
	CreatedAt          time.Time              `json:"created_at"`
	UpdatedAt          time.Time              `json:"updated_at"`
	LastActive         time.Time              `json:"last_active"`
	IsActive           bool                   `json:"is_active"`
	VerificationStatus bool                   `json:"verification_status"`
	ReputationScore    float64                `json:"reputation_score"`
}

func (u *User) ToResponse() *UserResponse {
	return &UserResponse{
		ID:                 u.ID,
		Username:           u.Username,
		Email:              u.Email,
		Role:               u.Role,
		DIDAddress:         u.DIDAddress,
		AnonymousMode:      u.AnonymousMode,
		ProfileData:        u.ProfileData,
		Preferences:        u.Preferences,
		CreatedAt:          u.CreatedAt,
		UpdatedAt:          u.UpdatedAt,
		LastActive:         u.LastActive,
		IsActive:           u.IsActive,
		VerificationStatus: u.VerificationStatus,
		ReputationScore:    u.ReputationScore,
	}
}

func (u *User) MarshalProfileData() ([]byte, error) {
	if u.ProfileData == nil {
		return []byte("{}"), nil
	}
	return json.Marshal(u.ProfileData)
}

func (u *User) MarshalPreferences() ([]byte, error) {
	if u.Preferences == nil {
		return []byte("{}"), nil
	}
	return json.Marshal(u.Preferences)
}