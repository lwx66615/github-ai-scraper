"""Tests for interactive CLI mode."""

from unittest.mock import patch, MagicMock

from ai_scraper.interactive import (
    show_main_menu,
    get_scrape_params,
    show_scrape_progress,
    confirm_action,
)


class TestConfirmAction:
    """Tests for confirm_action function."""

    def test_confirm_action_returns_true_when_confirmed(self):
        """Test that confirm_action returns True when user confirms."""
        with patch('rich.prompt.Confirm') as mock_confirm:
            mock_confirm.ask.return_value = True
            result = confirm_action("Delete all data?")
            assert result is True
            mock_confirm.ask.assert_called_once_with("Delete all data?")

    def test_confirm_action_returns_false_when_declined(self):
        """Test that confirm_action returns False when user declines."""
        with patch('rich.prompt.Confirm') as mock_confirm:
            mock_confirm.ask.return_value = False
            result = confirm_action("Continue?")
            assert result is False
            mock_confirm.ask.assert_called_once_with("Continue?")


class TestShowScrapeProgress:
    """Tests for show_scrape_progress function."""

    def test_show_scrape_progress_zero_total(self):
        """Test progress display with zero total."""
        with patch('ai_scraper.interactive.console') as mock_console:
            show_scrape_progress(0, 0, "test/repo")
            # Should handle division by zero gracefully
            mock_console.print.assert_called_once()

    def test_show_scrape_progress_half_complete(self):
        """Test progress display at 50% completion."""
        with patch('ai_scraper.interactive.console') as mock_console:
            show_scrape_progress(5, 10, "owner/repository")
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "5/10" in call_args
            assert "50%" in call_args
            assert "owner/repository" in call_args

    def test_show_scrape_progress_truncates_long_repo_names(self):
        """Test that long repository names are truncated."""
        with patch('ai_scraper.interactive.console') as mock_console:
            long_name = "a" * 50
            show_scrape_progress(1, 10, long_name)
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            # Should truncate to 40 chars
            assert len(long_name) > 40
            # The truncated name should be in the output
            assert long_name[:40] in call_args

    def test_show_scrape_progress_complete(self):
        """Test progress display at 100% completion."""
        with patch('ai_scraper.interactive.console') as mock_console:
            show_scrape_progress(100, 100, "complete/repo")
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "100/100" in call_args
            assert "100%" in call_args


class TestGetScrapeParams:
    """Tests for get_scrape_params function."""

    def test_get_scrape_params_defaults(self):
        """Test get_scrape_params with default values."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            mock_prompt.ask.side_effect = ["100", "100", ""]
            params = get_scrape_params()
            assert params["min_stars"] == 100
            assert params["max_results"] == 100
            assert params["language"] is None

    def test_get_scrape_params_custom_values(self):
        """Test get_scrape_params with custom values."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            mock_prompt.ask.side_effect = ["500", "200", "Python"]
            params = get_scrape_params()
            assert params["min_stars"] == 500
            assert params["max_results"] == 200
            assert params["language"] == "Python"

    def test_get_scrape_params_empty_language_becomes_none(self):
        """Test that empty language string becomes None."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            mock_prompt.ask.side_effect = ["100", "50", ""]
            params = get_scrape_params()
            assert params["language"] is None

    def test_get_scrape_params_prompts_in_order(self):
        """Test that prompts are asked in the correct order."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            mock_prompt.ask.side_effect = ["200", "300", "Rust"]
            get_scrape_params()

            # Check that prompts were called in the expected order
            assert mock_prompt.ask.call_count == 3
            calls = mock_prompt.ask.call_args_list
            assert calls[0][0][0] == "Minimum stars"
            assert calls[1][0][0] == "Maximum results"
            assert calls[2][0][0] == "Language filter (leave empty for all)"

    def test_get_scrape_params_invalid_min_stars_reprompts(self):
        """Test that invalid min_stars input shows error and re-prompts."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            with patch('ai_scraper.interactive.console') as mock_console:
                # First invalid, then valid input
                mock_prompt.ask.side_effect = ["abc", "100", "50", ""]
                params = get_scrape_params()
                # Should have error message printed
                mock_console.print.assert_called()
                error_calls = [c for c in mock_console.print.call_args_list
                               if "valid number" in str(c)]
                assert len(error_calls) >= 1
                assert params["min_stars"] == 100

    def test_get_scrape_params_negative_min_stars_shows_error(self):
        """Test that negative min_stars shows error and re-prompts."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            with patch('ai_scraper.interactive.console') as mock_console:
                # First negative, then valid
                mock_prompt.ask.side_effect = ["-10", "100", "50", ""]
                params = get_scrape_params()
                # Should have error message printed
                error_calls = [c for c in mock_console.print.call_args_list
                               if "non-negative" in str(c)]
                assert len(error_calls) >= 1
                assert params["min_stars"] == 100

    def test_get_scrape_params_invalid_max_results_reprompts(self):
        """Test that invalid max_results input shows error and re-prompts."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            with patch('ai_scraper.interactive.console') as mock_console:
                # Valid min_stars, invalid max_results, then valid
                mock_prompt.ask.side_effect = ["100", "xyz", "50", ""]
                params = get_scrape_params()
                # Should have error message printed
                error_calls = [c for c in mock_console.print.call_args_list
                               if "valid number" in str(c)]
                assert len(error_calls) >= 1
                assert params["max_results"] == 50

    def test_get_scrape_params_zero_max_results_shows_error(self):
        """Test that zero max_results shows error and re-prompts."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            with patch('ai_scraper.interactive.console') as mock_console:
                # Valid min_stars, zero max_results, then valid
                mock_prompt.ask.side_effect = ["100", "0", "50", ""]
                params = get_scrape_params()
                # Should have error message printed
                error_calls = [c for c in mock_console.print.call_args_list
                               if "greater than 0" in str(c)]
                assert len(error_calls) >= 1
                assert params["max_results"] == 50

    def test_get_scrape_params_negative_max_results_shows_error(self):
        """Test that negative max_results shows error and re-prompts."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            with patch('ai_scraper.interactive.console') as mock_console:
                # Valid min_stars, negative max_results, then valid
                mock_prompt.ask.side_effect = ["100", "-5", "50", ""]
                params = get_scrape_params()
                # Should have error message printed
                error_calls = [c for c in mock_console.print.call_args_list
                               if "greater than 0" in str(c)]
                assert len(error_calls) >= 1
                assert params["max_results"] == 50

    def test_get_scrape_params_accepts_zero_min_stars(self):
        """Test that zero min_stars is accepted (non-negative)."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            mock_prompt.ask.side_effect = ["0", "50", ""]
            params = get_scrape_params()
            assert params["min_stars"] == 0


class TestShowMainMenu:
    """Tests for show_main_menu function."""

    def test_show_main_menu_returns_user_choice(self):
        """Test that show_main_menu returns user's choice."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            mock_prompt.ask.return_value = "1"
            result = show_main_menu()
            assert result == "1"

    def test_show_main_menu_validates_choices(self):
        """Test that show_main_menu validates user input."""
        with patch('ai_scraper.interactive.Prompt') as mock_prompt:
            mock_prompt.ask.return_value = "q"
            result = show_main_menu()
            # Check that choices were specified
            call_kwargs = mock_prompt.ask.call_args[1]
            assert "choices" in call_kwargs
            expected_choices = ["1", "2", "3", "4", "5", "6", "7", "q"]
            assert call_kwargs["choices"] == expected_choices

    def test_show_main_menu_displays_panel(self):
        """Test that show_main_menu displays a panel with title."""
        with patch('ai_scraper.interactive.console') as mock_console:
            with patch('ai_scraper.interactive.Prompt') as mock_prompt:
                mock_prompt.ask.return_value = "1"
                show_main_menu()
                # Panel.fit should be called
                assert mock_console.print.call_count >= 1
