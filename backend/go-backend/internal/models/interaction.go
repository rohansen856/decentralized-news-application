package models

import (
	"time"

	"github.com/google/uuid"
)

type InteractionType string

const (
	InteractionLike    InteractionType = "like"
	InteractionDislike InteractionType = "dislike"
	InteractionSave    InteractionType = "save"
	InteractionShare   InteractionType = "share"
	InteractionView    InteractionType = "view"
	InteractionComment InteractionType = "comment"
)

type Interaction struct {
	ID                  uuid.UUID              `json:"id" db:"id"`
	UserID              uuid.UUID              `json:"user_id" db:"user_id"`
	ArticleID           uuid.UUID              `json:"article_id" db:"article_id"`
	InteractionType     InteractionType        `json:"interaction_type" db:"interaction_type"`
	InteractionStrength float64                `json:"interaction_strength" db:"interaction_strength" validate:"min=0,max=1"`
	ReadingProgress     float64                `json:"reading_progress" db:"reading_progress" validate:"min=0,max=1"`
	TimeSpent           int                    `json:"time_spent" db:"time_spent" validate:"min=0"`
	DeviceType          string                 `json:"device_type" db:"device_type"`
	SessionID           *string                `json:"session_id,omitempty" db:"session_id"`
	ContextData         map[string]interface{} `json:"context_data,omitempty" db:"context_data"`
	CreatedAt           time.Time              `json:"created_at" db:"created_at"`
}

type InteractionCreate struct {
	ArticleID           uuid.UUID              `json:"article_id" validate:"required"`
	InteractionType     InteractionType        `json:"interaction_type" validate:"required"`
	InteractionStrength float64                `json:"interaction_strength,omitempty" validate:"min=0,max=1"`
	ReadingProgress     float64                `json:"reading_progress,omitempty" validate:"min=0,max=1"`
	TimeSpent           int                    `json:"time_spent,omitempty" validate:"min=0"`
	DeviceType          string                 `json:"device_type,omitempty"`
	ContextData         map[string]interface{} `json:"context_data,omitempty"`
}

type InteractionResponse struct {
	ID                  uuid.UUID              `json:"id"`
	UserID              uuid.UUID              `json:"user_id"`
	ArticleID           uuid.UUID              `json:"article_id"`
	InteractionType     InteractionType        `json:"interaction_type"`
	InteractionStrength float64                `json:"interaction_strength"`
	ReadingProgress     float64                `json:"reading_progress"`
	TimeSpent           int                    `json:"time_spent"`
	DeviceType          string                 `json:"device_type"`
	SessionID           *string                `json:"session_id,omitempty"`
	ContextData         map[string]interface{} `json:"context_data,omitempty"`
	CreatedAt           time.Time              `json:"created_at"`
}

func (i *Interaction) ToResponse() *InteractionResponse {
	return &InteractionResponse{
		ID:                  i.ID,
		UserID:              i.UserID,
		ArticleID:           i.ArticleID,
		InteractionType:     i.InteractionType,
		InteractionStrength: i.InteractionStrength,
		ReadingProgress:     i.ReadingProgress,
		TimeSpent:           i.TimeSpent,
		DeviceType:          i.DeviceType,
		SessionID:           i.SessionID,
		ContextData:         i.ContextData,
		CreatedAt:           i.CreatedAt,
	}
}