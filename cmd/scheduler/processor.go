package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"sync"

	_ "github.com/mattn/go-sqlite3"
)

// Processor handles batch data processing
type Processor struct {
	db *sql.DB
}

// NewProcessor creates a new processor
func NewProcessor(dbPath string) (*Processor, error) {
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, err
	}

	return &Processor{db: db}, nil
}

// Close closes the database connection
func (p *Processor) Close() error {
	return p.db.Close()
}

// TrendResult represents a trend analysis result
type TrendResult struct {
	RepoID       int     `json:"repo_id"`
	RepoName     string  `json:"repo_name"`
	InitialStars int     `json:"initial_stars"`
	CurrentStars int     `json:"current_stars"`
	GrowthRate   float64 `json:"growth_rate"`
}

// CalculateTrends calculates star growth trends
func (p *Processor) CalculateTrends(repoIDs []int, days int) ([]TrendResult, error) {
	query := `
		SELECT
			r.id as repo_id,
			r.name as repo_name,
			(SELECT stars FROM snapshots WHERE repo_id = r.id
			 ORDER BY snapshot_at ASC LIMIT 1) as initial_stars,
			r.stars as current_stars
		FROM repositories r
		WHERE r.id IN (%s)
		HAVING initial_stars IS NOT NULL AND current_stars > initial_stars
		ORDER BY (CAST(current_stars AS FLOAT) / initial_stars - 1) DESC
	`

	// Build IN clause
	placeholders := ""
	args := make([]interface{}, len(repoIDs))
	for i, id := range repoIDs {
		if i > 0 {
			placeholders += ","
		}
		placeholders += "?"
		args[i] = id
	}

	rows, err := p.db.Query(fmt.Sprintf(query, placeholders), args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []TrendResult
	for rows.Next() {
		var tr TrendResult
		if err := rows.Scan(&tr.RepoID, &tr.RepoName, &tr.InitialStars, &tr.CurrentStars); err != nil {
			return nil, err
		}

		if tr.InitialStars > 0 {
			tr.GrowthRate = float64(tr.CurrentStars-tr.InitialStars) / float64(tr.InitialStars)
		}

		results = append(results, tr)
	}

	return results, nil
}

// AggregateStats calculates aggregate statistics
type AggregateStats struct {
	ByLanguage map[string]int `json:"by_language"`
	ByTopic    map[string]int `json:"by_topic"`
	TotalRepos int            `json:"total_repos"`
	TotalStars int            `json:"total_stars"`
}

// Aggregate calculates aggregate statistics
func (p *Processor) Aggregate() (*AggregateStats, error) {
	stats := &AggregateStats{
		ByLanguage: make(map[string]int),
		ByTopic:    make(map[string]int),
	}

	// Count by language
	rows, err := p.db.Query("SELECT language, COUNT(*) FROM repositories WHERE language IS NOT NULL GROUP BY language")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var lang string
		var count int
		if err := rows.Scan(&lang, &count); err != nil {
			return nil, err
		}
		stats.ByLanguage[lang] = count
	}

	// Count by topic (topics stored as JSON array)
	rows, err = p.db.Query("SELECT topics FROM repositories WHERE topics IS NOT NULL AND topics != '[]'")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var topicsJSON string
		if err := rows.Scan(&topicsJSON); err != nil {
			return nil, err
		}

		var topics []string
		if err := json.Unmarshal([]byte(topicsJSON), &topics); err == nil {
			for _, topic := range topics {
				stats.ByTopic[topic]++
			}
		}
	}

	// Total counts
	rows, err = p.db.Query("SELECT COUNT(*), COALESCE(SUM(stars), 0) FROM repositories")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	if rows.Next() {
		if err := rows.Scan(&stats.TotalRepos, &stats.TotalStars); err != nil {
			return nil, err
		}
	}

	return stats, nil
}

// ProcessBatch processes multiple repositories in parallel
func (p *Processor) ProcessBatch(repos []map[string]interface{}) error {
	var wg sync.WaitGroup
	errChan := make(chan error, len(repos))

	for _, repo := range repos {
		wg.Add(1)
		go func(r map[string]interface{}) {
			defer wg.Done()

			// Process each repo (e.g., calculate scores, update database)
			// This is a placeholder for actual processing logic
		}(repo)
	}

	wg.Wait()
	close(errChan)

	// Check for errors
	for err := range errChan {
		if err != nil {
			return err
		}
	}

	return nil
}
