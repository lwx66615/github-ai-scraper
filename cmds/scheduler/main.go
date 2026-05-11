package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	workers := flag.Int("workers", 4, "Number of worker goroutines")
	rateLimit := flag.Int("rate", 5000, "Requests per hour")
	flag.Parse()

	log.Printf("Starting scheduler with %d workers, %d req/hour rate limit", *workers, *rateLimit)

	scheduler := NewScheduler(*workers, *rateLimit)
	scheduler.Start()
	defer scheduler.Stop()

	// Handle shutdown signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Read tasks from stdin, write results to stdout
	go func() {
		scanner := bufio.NewScanner(os.Stdin)
		for scanner.Scan() {
			var task Task
			if err := json.Unmarshal(scanner.Bytes(), &task); err != nil {
				log.Printf("Error parsing task: %v", err)
				continue
			}

			if err := scheduler.Submit(task); err != nil {
				log.Printf("Error submitting task: %v", err)
			}
		}
	}()

	// Output results
	go func() {
		for result := range scheduler.GetResults() {
			data, err := json.Marshal(result)
			if err != nil {
				log.Printf("Error marshaling result: %v", err)
				continue
			}
			fmt.Println(string(data))
		}
	}()

	// Wait for shutdown
	<-sigChan
	log.Println("Shutting down...")
}
