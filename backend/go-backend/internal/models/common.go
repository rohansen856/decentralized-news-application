package models

import (
	"time"

	"github.com/google/uuid"
)

type BaseResponse struct {
	Success   bool      `json:"success"`
	Message   string    `json:"message"`
	Timestamp time.Time `json:"timestamp"`
}

type ErrorResponse struct {
	Success   bool                   `json:"success"`
	Message   string                 `json:"message"`
	ErrorCode *string                `json:"error_code,omitempty"`
	Details   map[string]interface{} `json:"details,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
}

type PaginatedResponse struct {
	Data    interface{} `json:"data"`
	Page    int         `json:"page"`
	PerPage int         `json:"per_page"`
	Total   int64       `json:"total"`
	Pages   int         `json:"pages"`
	HasNext bool        `json:"has_next"`
	HasPrev bool        `json:"has_prev"`
	BaseResponse
}

type TokenResponse struct {
	AccessToken string        `json:"access_token"`
	TokenType   string        `json:"token_type"`
	ExpiresIn   int           `json:"expires_in"`
	User        *UserResponse `json:"user"`
	BaseResponse
}

type HealthResponse struct {
	Status    string            `json:"status"`
	Timestamp time.Time         `json:"timestamp"`
	Services  map[string]string `json:"services"`
	Version   string            `json:"version"`
}

type RecommendationRequest struct {
	UserID          *uuid.UUID `json:"user_id,omitempty"`
	Limit           int        `json:"limit,omitempty" validate:"min=1,max=100"`
	Categories      []string   `json:"categories,omitempty"`
	ExcludeRead     bool       `json:"exclude_read,omitempty"`
	DiversityWeight float64    `json:"diversity_weight,omitempty" validate:"min=0,max=1"`
}

type RecommendationResponse struct {
	Recommendations []ArticleResponse `json:"recommendations"`
	ModelUsed       string            `json:"model_used"`
	GeneratedAt     time.Time         `json:"generated_at"`
	ExpiresAt       time.Time         `json:"expires_at"`
	BaseResponse
}

type SearchRequest struct {
	Query     string      `json:"query" validate:"required,min=1,max=500"`
	Categories []string   `json:"categories,omitempty"`
	Languages []string    `json:"languages,omitempty"`
	DateFrom  *time.Time  `json:"date_from,omitempty"`
	DateTo    *time.Time  `json:"date_to,omitempty"`
	AuthorID  *uuid.UUID  `json:"author_id,omitempty"`
	Limit     int         `json:"limit,omitempty" validate:"min=1,max=100"`
	Offset    int         `json:"offset,omitempty" validate:"min=0"`
	SortBy    string      `json:"sort_by,omitempty"`
}

type SearchResponse struct {
	Results         []ArticleResponse `json:"results"`
	TotalCount      int64             `json:"total_count"`
	Query           string            `json:"query"`
	ExecutionTimeMs float64           `json:"execution_time_ms"`
	BaseResponse
}

type AnalyticsRequest struct {
	UserID    *uuid.UUID `json:"user_id,omitempty"`
	ArticleID *uuid.UUID `json:"article_id,omitempty"`
	DateFrom  *time.Time `json:"date_from,omitempty"`
	DateTo    *time.Time `json:"date_to,omitempty"`
	Metrics   []string   `json:"metrics,omitempty"`
}

type AnalyticsResponse struct {
	Metrics map[string]interface{} `json:"metrics"`
	Period  map[string]interface{} `json:"period"`
	BaseResponse
}

func NewSuccessResponse(message string) *BaseResponse {
	return &BaseResponse{
		Success:   true,
		Message:   message,
		Timestamp: time.Now(),
	}
}

func NewErrorResponse(message string, errorCode *string, details map[string]interface{}) *ErrorResponse {
	return &ErrorResponse{
		Success:   false,
		Message:   message,
		ErrorCode: errorCode,
		Details:   details,
		Timestamp: time.Now(),
	}
}

func NewPaginatedResponse(data interface{}, page, perPage int, total int64) *PaginatedResponse {
	pages := int(total / int64(perPage))
	if total%int64(perPage) != 0 {
		pages++
	}

	return &PaginatedResponse{
		Data:    data,
		Page:    page,
		PerPage: perPage,
		Total:   total,
		Pages:   pages,
		HasNext: page < pages,
		HasPrev: page > 1,
		BaseResponse: BaseResponse{
			Success:   true,
			Message:   "Data retrieved successfully",
			Timestamp: time.Now(),
		},
	}
}