package middleware

import (
	"net/http"
	"strings"

	"news-app-go/internal/auth"
	"news-app-go/internal/models"

	"github.com/gin-gonic/gin"
)

func AuthRequired(jwtManager *auth.JWTManager) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, models.NewErrorResponse(
				"Authorization header is required",
				&[]string{"MISSING_AUTH_HEADER"}[0],
				nil,
			))
			c.Abort()
			return
		}

		tokenParts := strings.SplitN(authHeader, " ", 2)
		if len(tokenParts) != 2 || tokenParts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, models.NewErrorResponse(
				"Invalid authorization header format",
				&[]string{"INVALID_AUTH_FORMAT"}[0],
				nil,
			))
			c.Abort()
			return
		}

		claims, err := jwtManager.ValidateToken(tokenParts[1])
		if err != nil {
			c.JSON(http.StatusUnauthorized, models.NewErrorResponse(
				"Invalid or expired token",
				&[]string{"INVALID_TOKEN"}[0],
				map[string]interface{}{"error": err.Error()},
			))
			c.Abort()
			return
		}

		c.Set("user_id", claims.UserID)
		c.Set("user_email", claims.Email)
		c.Set("user_role", claims.Role)
		c.Set("username", claims.Username)
		c.Next()
	}
}

func OptionalAuth(jwtManager *auth.JWTManager) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		tokenParts := strings.SplitN(authHeader, " ", 2)
		if len(tokenParts) != 2 || tokenParts[0] != "Bearer" {
			c.Next()
			return
		}

		claims, err := jwtManager.ValidateToken(tokenParts[1])
		if err != nil {
			c.Next()
			return
		}

		c.Set("user_id", claims.UserID)
		c.Set("user_email", claims.Email)
		c.Set("user_role", claims.Role)
		c.Set("username", claims.Username)
		c.Next()
	}
}

func RequireRole(roles ...models.UserRole) gin.HandlerFunc {
	return func(c *gin.Context) {
		userRole, exists := c.Get("user_role")
		if !exists {
			c.JSON(http.StatusUnauthorized, models.NewErrorResponse(
				"User role not found in context",
				&[]string{"MISSING_USER_ROLE"}[0],
				nil,
			))
			c.Abort()
			return
		}

		role, ok := userRole.(models.UserRole)
		if !ok {
			c.JSON(http.StatusInternalServerError, models.NewErrorResponse(
				"Invalid user role format",
				&[]string{"INVALID_ROLE_FORMAT"}[0],
				nil,
			))
			c.Abort()
			return
		}

		for _, allowedRole := range roles {
			if role == allowedRole {
				c.Next()
				return
			}
		}

		c.JSON(http.StatusForbidden, models.NewErrorResponse(
			"Insufficient permissions",
			&[]string{"INSUFFICIENT_PERMISSIONS"}[0],
			map[string]interface{}{
				"required_roles": roles,
				"user_role":      role,
			},
		))
		c.Abort()
	}
}