package models

import (
	"time"

	"github.com/google/uuid"
)

type ArticleStatus string

const (
	StatusDraft     ArticleStatus = "draft"
	StatusPublished ArticleStatus = "published"
	StatusArchived  ArticleStatus = "archived"
	StatusBlocked   ArticleStatus = "blocked"
)

type Article struct {
	ID              uuid.UUID              `json:"id" db:"id"`
	AuthorID        *uuid.UUID             `json:"author_id,omitempty" db:"author_id"`
	Title           string                 `json:"title" db:"title" validate:"required,min=1,max=500"`
	Content         string                 `json:"content" db:"content" validate:"required,min=1"`
	Summary         *string                `json:"summary,omitempty" db:"summary" validate:"omitempty,max=1000"`
	Category        string                 `json:"category" db:"category" validate:"required,min=1,max=100"`
	Subcategory     *string                `json:"subcategory,omitempty" db:"subcategory" validate:"omitempty,max=100"`
	Tags            []string               `json:"tags" db:"tags"`
	Language        string                 `json:"language" db:"language"`
	Status          ArticleStatus          `json:"status" db:"status"`
	AnonymousAuthor bool                   `json:"anonymous_author" db:"anonymous_author"`
	ReadingTime     int                    `json:"reading_time" db:"reading_time"`
	WordCount       int                    `json:"word_count" db:"word_count"`
	PublishedAt     *time.Time             `json:"published_at,omitempty" db:"published_at"`
	CreatedAt       time.Time              `json:"created_at" db:"created_at"`
	UpdatedAt       time.Time              `json:"updated_at" db:"updated_at"`
	SourceURL       *string                `json:"source_url,omitempty" db:"source_url"`
	ImageURLs       []string               `json:"image_urls" db:"image_urls"`
	SEOKeywords     []string               `json:"seo_keywords" db:"seo_keywords"`
	EngagementScore float64                `json:"engagement_score" db:"engagement_score"`
	QualityScore    float64                `json:"quality_score" db:"quality_score"`
	TrendingScore   float64                `json:"trending_score" db:"trending_score"`
	ViewCount       int                    `json:"view_count" db:"view_count"`
	LikeCount       int                    `json:"like_count" db:"like_count"`
	CommentCount    int                    `json:"comment_count" db:"comment_count"`
	ShareCount      int                    `json:"share_count" db:"share_count"`
	Metadata        map[string]interface{} `json:"metadata,omitempty" db:"metadata"`
}

type ArticleCreate struct {
	Title           string                 `json:"title" validate:"required,min=1,max=500"`
	Content         string                 `json:"content" validate:"required,min=1"`
	Summary         *string                `json:"summary,omitempty" validate:"omitempty,max=1000"`
	Category        string                 `json:"category" validate:"required,min=1,max=100"`
	Subcategory     *string                `json:"subcategory,omitempty" validate:"omitempty,max=100"`
	Tags            []string               `json:"tags,omitempty"`
	Language        string                 `json:"language,omitempty"`
	AnonymousAuthor bool                   `json:"anonymous_author,omitempty"`
	Metadata        map[string]interface{} `json:"metadata,omitempty"`
}

type ArticleUpdate struct {
	Title           *string                `json:"title,omitempty" validate:"omitempty,min=1,max=500"`
	Content         *string                `json:"content,omitempty" validate:"omitempty,min=1"`
	Summary         *string                `json:"summary,omitempty" validate:"omitempty,max=1000"`
	Category        *string                `json:"category,omitempty" validate:"omitempty,min=1,max=100"`
	Subcategory     *string                `json:"subcategory,omitempty" validate:"omitempty,max=100"`
	Tags            []string               `json:"tags,omitempty"`
	Language        *string                `json:"language,omitempty" validate:"omitempty,max=10"`
	Status          *ArticleStatus         `json:"status,omitempty"`
	AnonymousAuthor *bool                  `json:"anonymous_author,omitempty"`
	Metadata        map[string]interface{} `json:"metadata,omitempty"`
}

type ArticleFilter struct {
	AuthorID    *uuid.UUID     `json:"author_id,omitempty"`
	Category    *string        `json:"category,omitempty"`
	Subcategory *string        `json:"subcategory,omitempty"`
	Status      *ArticleStatus `json:"status,omitempty"`
	Language    *string        `json:"language,omitempty"`
	Tags        []string       `json:"tags,omitempty"`
	DateFrom    *time.Time     `json:"date_from,omitempty"`
	DateTo      *time.Time     `json:"date_to,omitempty"`
	Limit       int            `json:"limit,omitempty" validate:"omitempty,min=1,max=100"`
	Offset      int            `json:"offset,omitempty" validate:"omitempty,min=0"`
	SortBy      string         `json:"sort_by,omitempty"`
}

type ArticleResponse struct {
	ID              uuid.UUID              `json:"id"`
	AuthorID        *uuid.UUID             `json:"author_id,omitempty"`
	Title           string                 `json:"title"`
	Content         string                 `json:"content"`
	Summary         *string                `json:"summary,omitempty"`
	Category        string                 `json:"category"`
	Subcategory     *string                `json:"subcategory,omitempty"`
	Tags            []string               `json:"tags"`
	Language        string                 `json:"language"`
	Status          ArticleStatus          `json:"status"`
	AnonymousAuthor bool                   `json:"anonymous_author"`
	ReadingTime     int                    `json:"reading_time"`
	WordCount       int                    `json:"word_count"`
	PublishedAt     *time.Time             `json:"published_at,omitempty"`
	CreatedAt       time.Time              `json:"created_at"`
	UpdatedAt       time.Time              `json:"updated_at"`
	SourceURL       *string                `json:"source_url,omitempty"`
	ImageURLs       []string               `json:"image_urls"`
	SEOKeywords     []string               `json:"seo_keywords"`
	EngagementScore float64                `json:"engagement_score"`
	QualityScore    float64                `json:"quality_score"`
	TrendingScore   float64                `json:"trending_score"`
	ViewCount       int                    `json:"view_count"`
	LikeCount       int                    `json:"like_count"`
	CommentCount    int                    `json:"comment_count"`
	ShareCount      int                    `json:"share_count"`
	Metadata        map[string]interface{} `json:"metadata,omitempty"`
}

func (a *Article) ToResponse() *ArticleResponse {
	return &ArticleResponse{
		ID:              a.ID,
		AuthorID:        a.AuthorID,
		Title:           a.Title,
		Content:         a.Content,
		Summary:         a.Summary,
		Category:        a.Category,
		Subcategory:     a.Subcategory,
		Tags:            a.Tags,
		Language:        a.Language,
		Status:          a.Status,
		AnonymousAuthor: a.AnonymousAuthor,
		ReadingTime:     a.ReadingTime,
		WordCount:       a.WordCount,
		PublishedAt:     a.PublishedAt,
		CreatedAt:       a.CreatedAt,
		UpdatedAt:       a.UpdatedAt,
		SourceURL:       a.SourceURL,
		ImageURLs:       a.ImageURLs,
		SEOKeywords:     a.SEOKeywords,
		EngagementScore: a.EngagementScore,
		QualityScore:    a.QualityScore,
		TrendingScore:   a.TrendingScore,
		ViewCount:       a.ViewCount,
		LikeCount:       a.LikeCount,
		CommentCount:    a.CommentCount,
		ShareCount:      a.ShareCount,
		Metadata:        a.Metadata,
	}
}