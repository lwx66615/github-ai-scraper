package main

import (
	"context"
	"sync"
	"time"
)

// TokenBucket implements a token bucket rate limiter
type TokenBucket struct {
	capacity   int
	tokens     float64
	refillRate float64 // tokens per second
	mu         sync.Mutex
	lastUpdate time.Time
}

// NewTokenBucket creates a new token bucket limiter
func NewTokenBucket(requestsPerHour int) *TokenBucket {
	effectiveLimit := int(float64(requestsPerHour) * 0.9) // 10% safety margin
	refillRate := float64(effectiveLimit) / 3600.0

	return &TokenBucket{
		capacity:   effectiveLimit,
		tokens:     float64(effectiveLimit),
		refillRate: refillRate,
		lastUpdate: time.Now(),
	}
}

// Wait blocks until a token is available or context is cancelled
func (tb *TokenBucket) Wait(ctx context.Context) error {
	tb.mu.Lock()
	tb.refill()
	tb.mu.Unlock()

	for {
		tb.mu.Lock()
		if tb.tokens >= 1.0 {
			tb.tokens -= 1.0
			tb.mu.Unlock()
			return nil
		}
		tb.mu.Unlock()

		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(100 * time.Millisecond):
			tb.mu.Lock()
			tb.refill()
			tb.mu.Unlock()
		}
	}
}

// TryAcquire attempts to acquire a token without blocking
func (tb *TokenBucket) TryAcquire() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	tb.refill()

	if tb.tokens >= 1.0 {
		tb.tokens -= 1.0
		return true
	}
	return false
}

// SetRate updates the rate limit
func (tb *TokenBucket) SetRate(requestsPerHour int) {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	effectiveLimit := int(float64(requestsPerHour) * 0.9)
	tb.capacity = effectiveLimit
	tb.refillRate = float64(effectiveLimit) / 3600.0
	if tb.tokens > float64(effectiveLimit) {
		tb.tokens = float64(effectiveLimit)
	}
}

// refill adds tokens based on elapsed time
func (tb *TokenBucket) refill() {
	now := time.Now()
	elapsed := now.Sub(tb.lastUpdate).Seconds()

	tb.tokens = min(float64(tb.capacity), tb.tokens+elapsed*tb.refillRate)
	tb.lastUpdate = now
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
