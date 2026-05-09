package main

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
)

// Task represents a task to be processed
type Task struct {
	ID      string                 `json:"id"`
	Type    string                 `json:"type"`
	Payload map[string]interface{} `json:"payload"`
}

// Result represents a task result
type Result struct {
	TaskID  string      `json:"task_id"`
	Success bool        `json:"success"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// Scheduler manages concurrent task processing
type Scheduler struct {
	maxWorkers  int
	taskQueue   chan Task
	resultQueue chan Result
	limiter     *TokenBucket
	wg          sync.WaitGroup
	ctx         context.Context
	cancel      context.CancelFunc
}

// NewScheduler creates a new scheduler
func NewScheduler(maxWorkers int, requestsPerHour int) *Scheduler {
	ctx, cancel := context.WithCancel(context.Background())

	return &Scheduler{
		maxWorkers:  maxWorkers,
		taskQueue:   make(chan Task, 100),
		resultQueue: make(chan Result, 100),
		limiter:     NewTokenBucket(requestsPerHour),
		ctx:         ctx,
		cancel:      cancel,
	}
}

// Start begins processing tasks
func (s *Scheduler) Start() {
	for i := 0; i < s.maxWorkers; i++ {
		s.wg.Add(1)
		go s.worker(i)
	}
}

// Stop gracefully shuts down the scheduler
func (s *Scheduler) Stop() {
	s.cancel()
	s.wg.Wait()
	close(s.taskQueue)
	close(s.resultQueue)
}

// Submit adds a task to the queue
func (s *Scheduler) Submit(task Task) error {
	select {
	case s.taskQueue <- task:
		return nil
	case <-s.ctx.Done():
		return fmt.Errorf("scheduler stopped")
	}
}

// GetResults returns the result channel
func (s *Scheduler) GetResults() <-chan Result {
	return s.resultQueue
}

// ProcessBatch processes multiple tasks and returns results
func (s *Scheduler) ProcessBatch(tasks []Task) []Result {
	results := make([]Result, 0, len(tasks))

	// Submit all tasks
	go func() {
		for _, task := range tasks {
			_ = s.Submit(task)
		}
	}()

	// Collect results
	received := 0
	for result := range s.resultQueue {
		results = append(results, result)
		received++
		if received >= len(tasks) {
			break
		}
	}

	return results
}

// worker processes tasks from the queue
func (s *Scheduler) worker(id int) {
	defer s.wg.Done()

	for {
		select {
		case <-s.ctx.Done():
			return
		case task, ok := <-s.taskQueue:
			if !ok {
				return
			}

			// Wait for rate limiter
			if err := s.limiter.Wait(s.ctx); err != nil {
				s.resultQueue <- Result{
					TaskID:  task.ID,
					Success: false,
					Error:   err.Error(),
				}
				continue
			}

			// Process task
			result := s.processTask(task)
			s.resultQueue <- result
		}
	}
}

// processTask handles a single task
func (s *Scheduler) processTask(task Task) Result {
	switch task.Type {
	case "process":
		return s.processData(task)
	default:
		return Result{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("unknown task type: %s", task.Type),
		}
	}
}

// processData processes repository data
func (s *Scheduler) processData(task Task) Result {
	// Extract repository data from payload
	data, err := json.Marshal(task.Payload)
	if err != nil {
		return Result{
			TaskID:  task.ID,
			Success: false,
			Error:   err.Error(),
		}
	}

	var repo struct {
		ID          int      `json:"id"`
		Name        string   `json:"name"`
		Stars       int      `json:"stars"`
		Topics      []string `json:"topics"`
		Description string   `json:"description"`
	}

	if err := json.Unmarshal(data, &repo); err != nil {
		return Result{
			TaskID:  task.ID,
			Success: false,
			Error:   err.Error(),
		}
	}

	// Calculate relevance score
	score := calculateRelevance(repo.Name, repo.Description, repo.Topics)

	return Result{
		TaskID:  task.ID,
		Success: true,
		Data: map[string]interface{}{
			"id":              repo.ID,
			"name":            repo.Name,
			"relevance_score": score,
		},
	}
}

// calculateRelevance calculates AI relevance score
func calculateRelevance(name, description string, topics []string) float64 {
	score := 0.0

	aiKeywords := []string{
		"ai", "machine learning", "deep learning", "neural network",
		"llm", "gpt", "transformer", "nlp", "computer vision",
		"pytorch", "tensorflow", "huggingface",
	}

	aiTopics := map[string]bool{
		"ai": true, "machine-learning": true, "deep-learning": true,
		"neural-network": true, "nlp": true, "computer-vision": true,
		"llm": true, "gpt": true, "pytorch": true, "tensorflow": true,
	}

	// Check keywords
	text := name + " " + description
	for _, kw := range aiKeywords {
		if contains(text, kw) {
			score += 0.2
		}
	}

	// Check topics
	for _, topic := range topics {
		if aiTopics[topic] {
			score += 0.15
		}
	}

	if score > 1.0 {
		score = 1.0
	}

	return score
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && containsHelper(s, substr))
}

func containsHelper(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
