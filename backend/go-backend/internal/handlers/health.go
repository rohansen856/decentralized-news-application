package handlers

import (
	"net/http"
	"time"

	"news-app-go/internal/database"
	"news-app-go/internal/models"

	"github.com/gin-gonic/gin"
)

type HealthHandler struct {
	db *database.Manager
}

func NewHealthHandler(db *database.Manager) *HealthHandler {
	return &HealthHandler{db: db}
}

func (h *HealthHandler) CheckHealth(c *gin.Context) {
	health := h.db.HealthCheck()
	
	status := "healthy"
	httpStatus := http.StatusOK
	
	services := make(map[string]string)
	for service, isHealthy := range health {
		if isHealthy {
			services[service] = "healthy"
		} else {
			services[service] = "unhealthy"
			status = "degraded"
			httpStatus = http.StatusServiceUnavailable
		}
	}

	response := &models.HealthResponse{
		Status:    status,
		Timestamp: time.Now(),
		Services:  services,
		Version:   "1.0.0",
	}

	c.JSON(httpStatus, response)
}