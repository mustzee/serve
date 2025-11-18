// Coding Assistant Example (Go version)
// Demonstrates using Local LLM for code generation and review
package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"strings"
	"time"

	llmclient "github.com/mustzee/serve/clients/go"
)

// CodingAssistant provides AI-powered coding assistance
type CodingAssistant struct {
	client *llmclient.Client
	model  string
}

// NewCodingAssistant creates a new coding assistant
func NewCodingAssistant(baseURL, model string) *CodingAssistant {
	if model == "" {
		model = "codellama"
	}

	return &CodingAssistant{
		client: llmclient.NewClient(baseURL),
		model:  model,
	}
}

// GenerateCode generates code based on a prompt
func (ca *CodingAssistant) GenerateCode(ctx context.Context, prompt, language string) (string, error) {
	req := &llmclient.ChatCompletionRequest{
		Model: ca.model,
		Messages: []llmclient.Message{
			{
				Role: "system",
				Content: fmt.Sprintf("You are an expert %s programmer. Generate clean, "+
					"efficient, and well-documented code.", language),
			},
			{
				Role:    "user",
				Content: fmt.Sprintf("Generate %s code for: %s", language, prompt),
			},
		},
		Temperature: 0.3,
		MaxTokens:   2048,
	}

	resp, err := ca.client.Chat(ctx, req)
	if err != nil {
		return "", err
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response from model")
	}

	return resp.Choices[0].Message.Content, nil
}

// ReviewCode reviews code and provides suggestions
func (ca *CodingAssistant) ReviewCode(ctx context.Context, code, language string) (string, error) {
	req := &llmclient.ChatCompletionRequest{
		Model: ca.model,
		Messages: []llmclient.Message{
			{
				Role: "system",
				Content: "You are a senior code reviewer. Provide constructive feedback " +
					"on code quality, potential bugs, performance, and best practices.",
			},
			{
				Role: "user",
				Content: fmt.Sprintf("Review this %s code:\n\n```%s\n%s\n```",
					language, language, code),
			},
		},
		Temperature: 0.5,
		MaxTokens:   2048,
	}

	resp, err := ca.client.Chat(ctx, req)
	if err != nil {
		return "", err
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response from model")
	}

	return resp.Choices[0].Message.Content, nil
}

// ChatStream performs interactive chat with streaming
func (ca *CodingAssistant) ChatStream(ctx context.Context, prompt string) error {
	req := &llmclient.ChatCompletionRequest{
		Model: ca.model,
		Messages: []llmclient.Message{
			{
				Role: "system",
				Content: "You are a helpful coding assistant for Python and Go.",
			},
			{
				Role:    "user",
				Content: prompt,
			},
		},
		Temperature: 0.7,
		MaxTokens:   2048,
		Stream:      true,
	}

	fmt.Print("Assistant: ")
	contentChan, errorChan := ca.client.StreamChat(ctx, req)

	for {
		select {
		case content, ok := <-contentChan:
			if !ok {
				fmt.Println()
				return nil
			}
			fmt.Print(content)
		case err := <-errorChan:
			if err != nil {
				return err
			}
		case <-ctx.Done():
			return ctx.Err()
		}
	}
}

func main() {
	fmt.Println("=== Coding Assistant Demo (Go) ===\n")

	assistant := NewCodingAssistant("http://localhost:8000", "codellama")
	ctx := context.Background()

	// Check server health
	health, err := assistant.client.Health(ctx)
	if err != nil {
		fmt.Printf("✗ Server not available: %v\n", err)
		fmt.Println("Please start the server first")
		return
	}

	fmt.Printf("✓ Server Status: %s\n", health.Status)
	fmt.Printf("✓ Backend: %s\n", health.Backend)
	fmt.Printf("✓ Models: %s\n\n", strings.Join(health.ModelsLoaded, ", "))

	// Example 1: Generate code
	fmt.Println("1. Generate Code")
	fmt.Println(strings.Repeat("-", 50))
	prompt := "Create a function to implement binary search in Go"
	fmt.Printf("Prompt: %s\n\n", prompt)

	code, err := assistant.GenerateCode(ctx, prompt, "go")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("Generated Code:\n%s\n", code)
	}

	// Example 2: Review code
	fmt.Println("\n2. Review Code")
	fmt.Println(strings.Repeat("-", 50))
	sampleCode := `
func sum(nums []int) int {
    total := 0
    for i := 0; i < len(nums); i++ {
        total = total + nums[i]
    }
    return total
}
`
	fmt.Printf("Code to review:%s\n", sampleCode)

	review, err := assistant.ReviewCode(ctx, strings.TrimSpace(sampleCode), "go")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("Review:\n%s\n", review)
	}

	// Example 3: Interactive chat
	fmt.Println("\n3. Interactive Chat (type 'exit' to quit)")
	fmt.Println(strings.Repeat("-", 50))

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("\nYou: ")
		if !scanner.Scan() {
			break
		}

		input := strings.TrimSpace(scanner.Text())
		if input == "" {
			continue
		}

		if strings.ToLower(input) == "exit" || strings.ToLower(input) == "quit" {
			fmt.Println("Goodbye!")
			break
		}

		ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
		if err := assistant.ChatStream(ctx, input); err != nil {
			fmt.Printf("Error: %v\n", err)
		}
		cancel()
	}
}
