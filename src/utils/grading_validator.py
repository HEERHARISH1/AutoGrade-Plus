"""
Grading validation utilities to ensure mathematical and logical correctness
"""

import json
import re


def validate_and_fix_grading(grading_output):
    """
    Validates grading output for mathematical correctness and fixes issues.
    
    Args:
        grading_output: String containing JSON grading result
        
    Returns:
        dict: Validated and corrected grading result
    """
    try:
        # Extract JSON from output with robust parsing
        json_str = extract_json_from_text(grading_output)
        
        if not json_str:
            raise ValueError("No valid JSON found in output")
        
        # Parse JSON
        data = json.loads(json_str)
        
        # Validate and fix
        validated = validate_grading_data(data)
        
        return validated
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing error: {e}")
        print(f"📄 Raw output (first 500 chars): {grading_output[:500]}")
        return {
            "score": 0,
            "max_score": 0,
            "feedback": f"Error parsing grading output: {str(e)}",
            "breakdown": {},
            "validation_errors": [f"JSON decode error at position {e.pos}: {e.msg}"]
        }
    except Exception as e:
        print(f"⚠️ Validation error: {e}")
        print(f"📄 Raw output (first 500 chars): {grading_output[:500]}")
        return {
            "score": 0,
            "max_score": 0,
            "feedback": f"Error parsing grading output: {str(e)}",
            "breakdown": {},
            "validation_errors": [str(e)]
        }


def extract_json_from_text(text):
    """
    Extracts JSON from text that may contain markdown, extra text, or formatting.
    
    Args:
        text: String that may contain JSON
        
    Returns:
        str: Extracted JSON string or None
    """
    if not text or not isinstance(text, str):
        return None
    
    # Remove markdown code blocks (multiple variations)
    text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*', '', text)
    text = re.sub(r'`', '', text)
    
    # Remove common prefixes
    text = re.sub(r'^(Here\'s the grading|The grading result is|Result:)\s*', '', text, flags=re.IGNORECASE)
    
    # Try to find JSON object with multiple strategies
    strategies = [
        # Strategy 1: Look for complete JSON with proper nesting
        lambda t: re.search(r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}', t, re.DOTALL),
        
        # Strategy 2: Find outermost braces
        lambda t: find_outermost_braces(t),
        
        # Strategy 3: Simple greedy match
        lambda t: re.search(r'\{.*\}', t, re.DOTALL),
    ]
    
    for strategy in strategies:
        try:
            match = strategy(text)
            if match:
                if isinstance(match, str):
                    json_candidate = match
                else:
                    json_candidate = match.group(0)
                
                # Clean up the candidate
                json_candidate = json_candidate.strip()
                
                # Remove trailing commas before closing braces/brackets
                json_candidate = re.sub(r',(\s*[}\]])', r'\1', json_candidate)
                
                # Try to parse it
                try:
                    parsed = json.loads(json_candidate)
                    # Verify it has expected structure
                    if isinstance(parsed, dict):
                        return json_candidate
                except json.JSONDecodeError as e:
                    # Try to fix common issues
                    fixed = try_fix_json(json_candidate)
                    if fixed:
                        try:
                            json.loads(fixed)
                            return fixed
                        except:
                            continue
                    continue
        except Exception:
            continue
    
    # Last resort: try to find any dict-like structure
    print("⚠️ Standard JSON extraction failed, trying fallback methods...")
    print(f"📄 Text preview: {text[:300]}")
    
    return None


def find_outermost_braces(text):
    """Find the outermost pair of braces in text"""
    start = text.find('{')
    if start == -1:
        return None
    
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    
    return None


def try_fix_json(json_str):
    """Attempt to fix common JSON formatting issues"""
    try:
        # Fix single quotes to double quotes (but not in values)
        # This is tricky, so we'll use a simple heuristic
        fixed = json_str
        
        # Remove trailing commas
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        
        # Fix unquoted keys (simple pattern)
        fixed = re.sub(r'(\w+)(\s*):', r'"\1"\2:', fixed)
        
        # Remove duplicate quotes
        fixed = re.sub(r'"{2,}', '"', fixed)
        
        return fixed
    except:
        return None


def validate_grading_data(data):
    """
    Validates and corrects grading data for mathematical accuracy.
    
    Checks:
    1. No criterion points exceed max points
    2. Final score equals sum of breakdown points
    3. All required fields are present
    
    Returns:
        dict: Corrected grading data with validation_notes
    """
    validation_notes = []
    
    # Ensure required fields exist
    if 'breakdown' not in data:
        data['breakdown'] = {}
        validation_notes.append("Missing breakdown field - added empty breakdown")
    
    if 'score' not in data:
        data['score'] = 0
        validation_notes.append("Missing score field - set to 0")
    
    if 'max_score' not in data:
        data['max_score'] = 0
        validation_notes.append("Missing max_score field - set to 0")
    
    if 'feedback' not in data:
        data['feedback'] = "No feedback provided"
        validation_notes.append("Missing feedback field")
    
    # Validate breakdown
    breakdown = data.get('breakdown', {})
    corrected_breakdown = {}
    actual_sum = 0
    total_max = 0
    
    for criterion, details in breakdown.items():
        if not isinstance(details, dict):
            validation_notes.append(f"Invalid format for criterion '{criterion}' - skipped")
            continue
        
        awarded = details.get('points', 0)
        max_points = details.get('max', 0)
        comment = details.get('comment', '')
        
        # Ensure numeric values
        try:
            awarded = float(awarded)
            max_points = float(max_points)
        except (ValueError, TypeError):
            validation_notes.append(f"Non-numeric values in '{criterion}' - set to 0")
            awarded = 0
            max_points = 0
        
        # RULE 1: Awarded points cannot exceed max points
        if awarded > max_points:
            validation_notes.append(
                f"❌ MATH ERROR: '{criterion}' had {awarded} points but max is {max_points}. "
                f"Corrected to {max_points}."
            )
            awarded = max_points
        
        # Ensure non-negative
        if awarded < 0:
            validation_notes.append(f"Negative points in '{criterion}' - set to 0")
            awarded = 0
        
        if max_points < 0:
            validation_notes.append(f"Negative max in '{criterion}' - set to 0")
            max_points = 0
        
        # Round to 2 decimal places to avoid floating point issues
        awarded = round(awarded, 2)
        max_points = round(max_points, 2)
        
        corrected_breakdown[criterion] = {
            'points': awarded,
            'max': max_points,
            'comment': comment
        }
        
        actual_sum += awarded
        total_max += max_points
    
    # Round the sum to avoid floating point precision issues
    actual_sum = round(actual_sum, 2)
    total_max = round(total_max, 2)
    
    # RULE 2: Final score must equal sum of breakdown points
    reported_score = data.get('score', 0)
    try:
        reported_score = float(reported_score)
    except (ValueError, TypeError):
        reported_score = 0
        validation_notes.append("Invalid score format - set to 0")
    
    if abs(reported_score - actual_sum) > 0.01:  # Allow tiny floating point difference
        validation_notes.append(
            f"❌ MATH ERROR: Reported score was {reported_score} but sum of breakdown is {actual_sum}. "
            f"Corrected to {actual_sum}."
        )
        reported_score = actual_sum
    
    # RULE 3: Validate max_score
    reported_max = data.get('max_score', 0)
    try:
        reported_max = float(reported_max)
    except (ValueError, TypeError):
        reported_max = 0
        validation_notes.append("Invalid max_score format - set to 0")
    
    if abs(reported_max - total_max) > 0.01:
        validation_notes.append(
            f"⚠️ Max score mismatch: Reported {reported_max} but breakdown total is {total_max}. "
            f"Corrected to {total_max}."
        )
        reported_max = total_max
    
    # Build corrected result
    corrected_data = {
        'score': reported_score,
        'max_score': reported_max,
        'feedback': data.get('feedback', ''),
        'breakdown': corrected_breakdown
    }
    
    # Add validation notes if any corrections were made
    if validation_notes:
        corrected_data['validation_notes'] = validation_notes
        print("\n⚠️ GRADING VALIDATION CORRECTIONS:")
        for note in validation_notes:
            print(f"  - {note}")
    else:
        print("✅ Grading validation passed - no corrections needed")
    
    return corrected_data


def format_validated_grading(validated_data):
    """
    Formats validated grading data into a nice markdown report.
    
    Args:
        validated_data: Validated grading dictionary
        
    Returns:
        str: Formatted markdown report
    """
    score = validated_data.get('score', 0)
    max_score = validated_data.get('max_score', 0)
    feedback = validated_data.get('feedback', 'No feedback provided.')
    breakdown = validated_data.get('breakdown', {})
    validation_notes = validated_data.get('validation_notes', [])
    
    # Build report
    md = f"### 🎓 **Final Score: {score} / {max_score}**\n\n"
    
    # Add validation warnings if any
    if validation_notes:
        md += "⚠️ **Validation Corrections Applied:**\n"
        for note in validation_notes:
            md += f"- {note}\n"
        md += "\n"
    
    md += f"#### 📝 **Feedback Summary**\n"
    md += f"{feedback}\n\n"
    
    md += f"#### 📊 **Detailed Breakdown**\n"
    md += "| Criterion | Score | Comments |\n"
    md += "| :--- | :---: | :--- |\n"
    
    for criterion, details in breakdown.items():
        points = details.get('points', 0)
        max_pts = details.get('max', 0)
        comment = details.get('comment', '')
        md += f"| **{criterion}** | {points}/{max_pts} | {comment} |\n"
    
    # Add mathematical verification
    md += f"\n#### ✅ **Mathematical Verification**\n"
    md += f"- Sum of breakdown points: {score}\n"
    md += f"- Reported final score: {score}\n"
    md += f"- **Status:** {'✅ Correct' if not validation_notes else '⚠️ Corrected'}\n"
    
    return md
