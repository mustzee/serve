// Package llmclient provides a Go client for Local LLM Serve API
package llmclient

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"strings"

	"github.com/go-resty/resty/v2"
)

// Message represents a chat message
type Message struct {
	Role    string `json:"role"`    // system, user, assistant
	Content string `json:"content"`
}

// ChatCompletionRequest represents a chat completion request
type ChatCompletionRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Temperature float64   `json:"temperature,omitempty"`
	MaxTokens   int       `json:"max_tokens,omitempty"`
	Stream      bool      `json:"stream,omitempty"`
	TopP        float64   `json:"top_p,omitempty"`
}

// ChatCompletionResponse represents a chat completion response
type ChatCompletionResponse struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Created int64  `json:"created"`
	Model   string `json:"model"`
	Choices []struct {
		Index   int `json:"index"`
		Message struct {
			Role    string `json:"role"`
			Content string `json:"content"`
		} `json:"message"`
		FinishReason string `json:"finish_reason"`
	} `json:"choices"`
	Usage struct {
		PromptTokens     int `json:"prompt_tokens"`
		CompletionTokens int `json:"completion_tokens"`
		TotalTokens      int `json:"total_tokens"`
	} `json:"usage"`
}

// HealthResponse represents server health status
type HealthResponse struct {
	Status       string   `json:"status"`
	Backend      string   `json:"backend"`
	ModelsLoaded []string `json:"models_loaded"`
}

// ModelInfo represents model information
type ModelInfo struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	OwnedBy string `json:"owned_by"`
}

// Client is the LLM API client
type Client struct {
	baseURL string
	client  *resty.Client
}

// NewClient creates a new LLM client
func NewClient(baseURL string) *Client {
	if baseURL == "" {
		baseURL = "http://localhost:8000"
	}

	return &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		client:  resty.New(),
	}
}

// Health checks server health
func (c *Client) Health(ctx context.Context) (*HealthResponse, error) {
	var result HealthResponse

	resp, err := c.client.R().
		SetContext(ctx).
		SetResult(&result).
		Get(c.baseURL + "/health")

	if err != nil {
		return nil, err
	}

	if resp.IsError() {
		return nil, fmt.Errorf("health check failed: %s", resp.Status())
	}

	return &result, nil
}

// ListModels lists available models
func (c *Client) ListModels(ctx context.Context) ([]string, error) {
	var models []ModelInfo

	resp, err := c.client.R().
		SetContext(ctx).
		SetResult(&models).
		Get(c.baseURL + "/v1/models")

	if err != nil {
		return nil, err
	}

	if resp.IsError() {
		return nil, fmt.Errorf("list models failed: %s", resp.Status())
	}

	modelIDs := make([]string, len(models))
	for i, model := range models {
		modelIDs[i] = model.ID
	}

	return modelIDs, nil
}

// Chat sends a chat completion request
func (c *Client) Chat(ctx context.Context, req *ChatCompletionRequest) (*ChatCompletionResponse, error) {
	var result ChatCompletionResponse

	resp, err := c.client.R().
		SetContext(ctx).
		SetBody(req).
		SetResult(&result).
		Post(c.baseURL + "/v1/chat/completions")

	if err != nil {
		return nil, err
	}

	if resp.IsError() {
		return nil, fmt.Errorf("chat completion failed: %s", resp.Status())
	}

	return &result, nil
}

// StreamChat sends a streaming chat completion request
func (c *Client) StreamChat(ctx context.Context, req *ChatCompletionRequest) (<-chan string, <-chan error) {
	contentChan := make(chan string, 100)
	errorChan := make(chan error, 1)

	req.Stream = true

	go func() {
		defer close(contentChan)
		defer close(errorChan)

		resp, err := c.client.R().
			SetContext(ctx).
			SetBody(req).
			SetDoNotParseResponse(true).
			Post(c.baseURL + "/v1/chat/completions")

		if err != nil {
			errorChan <- err
			return
		}

		defer resp.RawBody().Close()

		if resp.IsError() {
			errorChan <- fmt.Errorf("stream chat failed: %s", resp.Status())
			return
		}

		scanner := bufio.NewScanner(resp.RawBody())
		for scanner.Scan() {
			line := scanner.Text()
			if strings.HasPrefix(line, "data: ") {
				data := strings.TrimPrefix(line, "data: ")
				if data == "[DONE]" {
					break
				}

				var chunk struct {
					Choices []struct {
						Delta struct {
							Content string `json:"content"`
						} `json:"delta"`
					} `json:"choices"`
				}

				if err := json.Unmarshal([]byte(data), &chunk); err != nil {
					continue
				}

				if len(chunk.Choices) > 0 {
					content := chunk.Choices[0].Delta.Content
					if content != "" {
						select {
						case contentChan <- content:
						case <-ctx.Done():
							return
						}
					}
				}
			}
		}

		if err := scanner.Err(); err != nil && err != io.EOF {
			errorChan <- err
		}
	}()

	return contentChan, errorChan
}

// Complete is a simple completion method
func (c *Client) Complete(ctx context.Context, prompt, model string, temperature float64, maxTokens int) (string, error) {
	req := &ChatCompletionRequest{
		Model: model,
		Messages: []Message{
			{Role: "user", Content: prompt},
		},
		Temperature: temperature,
		MaxTokens:   maxTokens,
		Stream:      false,
	}

	resp, err := c.Chat(ctx, req)
	if err != nil {
		return "", err
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no completion returned")
	}

	return resp.Choices[0].Message.Content, nil
}
