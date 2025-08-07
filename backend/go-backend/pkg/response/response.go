package response

import (
	"net/http"

	"news-app-go/internal/models"

	"github.com/gin-gonic/gin"
)

func Success(c *gin.Context, data interface{}, message string) {
	response := models.NewSuccessResponse(message)
	c.JSON(http.StatusOK, gin.H{
		"success":   response.Success,
		"message":   response.Message,
		"timestamp": response.Timestamp,
		"data":      data,
	})
}

func Created(c *gin.Context, data interface{}, message string) {
	response := models.NewSuccessResponse(message)
	c.JSON(http.StatusCreated, gin.H{
		"success":   response.Success,
		"message":   response.Message,
		"timestamp": response.Timestamp,
		"data":      data,
	})
}

func Error(c *gin.Context, statusCode int, message string, errorCode *string, details map[string]interface{}) {
	response := models.NewErrorResponse(message, errorCode, details)
	c.JSON(statusCode, response)
}

func BadRequest(c *gin.Context, message string, details map[string]interface{}) {
	errorCode := "BAD_REQUEST"
	Error(c, http.StatusBadRequest, message, &errorCode, details)
}

func Unauthorized(c *gin.Context, message string) {
	errorCode := "UNAUTHORIZED"
	Error(c, http.StatusUnauthorized, message, &errorCode, nil)
}

func Forbidden(c *gin.Context, message string) {
	errorCode := "FORBIDDEN"
	Error(c, http.StatusForbidden, message, &errorCode, nil)
}

func NotFound(c *gin.Context, message string) {
	errorCode := "NOT_FOUND"
	Error(c, http.StatusNotFound, message, &errorCode, nil)
}

func Conflict(c *gin.Context, message string, details map[string]interface{}) {
	errorCode := "CONFLICT"
	Error(c, http.StatusConflict, message, &errorCode, details)
}

func InternalServerError(c *gin.Context, message string, details map[string]interface{}) {
	errorCode := "INTERNAL_SERVER_ERROR"
	Error(c, http.StatusInternalServerError, message, &errorCode, details)
}

func ValidationError(c *gin.Context, errors map[string]string) {
	details := map[string]interface{}{
		"validation_errors": errors,
	}
	BadRequest(c, "Validation failed", details)
}

func Paginated(c *gin.Context, data interface{}, page, perPage int, total int64, message string) {
	response := models.NewPaginatedResponse(data, page, perPage, total)
	c.JSON(http.StatusOK, response)
}