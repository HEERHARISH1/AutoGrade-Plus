"""
Intelligent content analyzer that uses AI to detect what type of content is in each file
"""

def analyze_content_type(content, api_key, model_provider="groq"):
    """
    Use AI to determine if content contains Question, Rubric, Answer, or ANY combination.
    Returns: list of detected types ['question', 'rubric', 'answer']
    """
    from src.agent.react_engine import GradingAgent
    
    # UNIVERSAL PROMPT: Detect ALL components present in the text
    prompt = f"""You are an expert educational content analyzer. Your job is to identify what components are present in the following file content.

POSSIBLE COMPONENTS:
1. **QUESTION:** Assignment instructions, problem descriptions, tasks to solve.
2. **RUBRIC:** Grading criteria, points breakdown, marking scheme.
3. **ANSWER:** Student's work, code solution, written response, completed task.

INSTRUCTIONS:
- Read the text carefully.
- Determine WHICH of the above are present.
- A single file can contain ONE, TWO, or ALL THREE components.
- **CRITICAL:** Distinguish between "Instructions" (Question) and "Completed Work" (Answer).
  - "Write a function..." = QUESTION
  - "def my_function():..." = ANSWER
  - "Points: 10/10" = RUBRIC

TEXT TO ANALYZE:
{content[:10000]}

RESPOND WITH A JSON LIST of detected types. 
Options: "question", "rubric", "answer".
Example: ["question", "rubric"] or ["answer"] or ["question", "rubric", "answer"]
"""

    try:
        agent = GradingAgent(model_provider=model_provider, api_key=api_key)
        response = agent.llm.invoke(prompt)
        
        result_str = str(response.content if hasattr(response, 'content') else response).lower()
        
        detected = []
        if 'question' in result_str: detected.append('question')
        if 'rubric' in result_str: detected.append('rubric')
        if 'answer' in result_str or 'student' in result_str or 'solution' in result_str: detected.append('answer')
        
        # Fallback if JSON parsing fails but keywords exist
        if not detected:
            return analyze_with_heuristics(content)
            
        return detected
            
    except Exception as e:
        print(f"⚠️ AI analysis failed: {e}, falling back to heuristics")
        return analyze_with_heuristics(content)


def analyze_with_heuristics(content):
    """
    Fallback heuristic detection with improved logic
    """
    content_lower = content.lower()
    detected = []
    
    # Check for student ID pattern first (strong indicator of answer)
    import re
    has_student_id = bool(re.search(r'\b[iI]\d{6}\b', content))
    
    # Answer indicators - look for ACTUAL code, not just mentions
    # Check for code patterns that indicate implementation
    has_code_implementation = bool(re.search(r'(def\s+\w+\s*\(|class\s+\w+\s*[:(]|import\s+\w+|return\s+\w)', content))
    
    answer_indicators = [
        'my solution', 'i implemented', 'submitted by', 'group members'
    ]
    has_answer_text = any(kw in content_lower for kw in answer_indicators)
    
    # Rubric indicators - strong keywords
    rubric_strong = ['grading rubric', 'rubric', 'grading criteria', 'total points:', 'criteria:']
    rubric_weak = ['points:', 'marks:', 'score', 'evaluation']
    has_rubric_strong = any(kw in content_lower for kw in rubric_strong)
    has_rubric_weak = any(kw in content_lower for kw in rubric_weak)
    
    # Question indicators - strong keywords
    question_strong = ['assignment', 'task:', 'requirements:', 'write a function', 'implement']
    question_weak = ['problem:', 'question', 'exercise', 'submission']
    has_question_strong = any(kw in content_lower for kw in question_strong)
    has_question_weak = any(kw in content_lower for kw in question_weak)
    
    # Decision logic with priority
    # 1. If student ID found AND has code implementation, it's definitely an answer
    if has_student_id and has_code_implementation:
        detected.append('answer')
        return detected
    
    # 2. If has strong rubric indicators, it's a rubric
    if has_rubric_strong:
        detected.append('rubric')
        # Check if it also has question
        if has_question_strong and not has_code_implementation:
            detected.append('question')
        return detected
    
    # 3. If has strong question indicators WITHOUT code implementation, it's a question
    if has_question_strong and not has_code_implementation:
        detected.append('question')
        # Check if it also mentions rubric
        if has_rubric_weak:
            detected.append('rubric')
        return detected
    
    # 4. If has actual code implementation (def, class, import, return), it's likely an answer
    if has_code_implementation or has_answer_text:
        detected.append('answer')
        return detected
    
    # 5. If has weak rubric indicators
    if has_rubric_weak and not has_code_implementation:
        detected.append('rubric')
        if has_question_weak:
            detected.append('question')
        return detected
    
    # 6. If has weak question indicators
    if has_question_weak:
        detected.append('question')
        return detected
    
    # 7. Fallback - try to infer from content structure
    if len(content.strip()) > 50:
        # If mentions "write" or "implement" without code, assume question
        if any(word in content_lower for word in ['write a', 'implement a', 'create a']) and not has_code_implementation:
            detected.append('question')
        # If mentions points/marks without code, assume rubric
        elif any(word in content_lower for word in ['point', 'mark', 'grade']) and not has_code_implementation:
            detected.append('rubric')
        # Otherwise default to question
        else:
            detected.append('question')
    
    return detected if detected else ['question']  # Default to question if unsure


def calculate_heuristic_confidence(content, detected_types):
    """
    Calculate confidence score (0-100) for heuristic detection.
    Higher score = more certain about the detection.
    """
    content_lower = content.lower()
    confidence = 50  # Base confidence
    
    # Strong indicators boost confidence
    strong_indicators = {
        'rubric': ['rubric', 'grading criteria', 'points:', 'marks:', 'total:', 'max points'],
        'question': ['assignment', 'task:', 'problem:', 'write a', 'implement', 'question:', 'exercise'],
        'answer': ['def ', 'class ', 'import ', 'return ', 'student id', 'submitted by']
    }
    
    for dtype in detected_types:
        if dtype in strong_indicators:
            matches = sum(1 for indicator in strong_indicators[dtype] if indicator in content_lower)
            confidence += matches * 10  # +10 per strong indicator
    
    # Length-based confidence (longer content = more reliable)
    if len(content) > 1000:
        confidence += 10
    elif len(content) > 500:
        confidence += 5
    
    # Multiple detections lower confidence (ambiguous)
    if len(detected_types) > 1:
        confidence -= 15
    
    # Cap at 100
    return min(confidence, 100)


def smart_categorize_files(files_content, api_key, model_provider="groq"):
    """
    Universally categorize files by analyzing their CONTENT.
    Handles any combination: 1 file (all), 2 files (split), 3 files (separate).
    Uses heuristics first to save API calls, only uses AI if uncertain.
    
    IMPORTANT: For content detection, we ALWAYS use Groq (if API key available),
    regardless of which model is used for grading. This ensures consistent detection.
    """
    print(f"\n🔍 STARTING INTELLIGENT FILE ANALYSIS...")
    print(f"📊 Received {len(files_content)} file(s) to analyze:")
    for fname, fcontent in files_content.items():
        print(f"   - {fname}: {len(fcontent)} chars")
    
    categorized = {
        'question': '',
        'rubric': '',
        'answer': ''
    }
    
    file_classifications = {}
    
    for filename, content in files_content.items():
        if not content or len(content.strip()) < 10:
            print(f"⚠️ Skipping empty file: {filename}")
            continue
            
        print(f"📄 Analyzing content of: {filename} ({len(content)} chars)...")
        print(f"   📝 Preview: {content[:100].replace(chr(10), ' ')}...")
        
        # 1. Try heuristics first (fast, no API call)
        heuristic_types = analyze_with_heuristics(content)
        confidence = calculate_heuristic_confidence(content, heuristic_types)
        
        print(f"   🔍 Heuristic detection: {', '.join(heuristic_types).upper()} (confidence: {confidence}%)")
        
        # 2. Only use AI if heuristics are uncertain (< 70% confidence)
        if confidence < 70 and api_key:
            print(f"   🤖 Low confidence, using AI for verification...")
            try:
                # ALWAYS use Groq for content detection (most reliable)
                # Even if grading model is LoRA/finetuned
                detection_provider = "groq" if api_key else model_provider
                detected_types = analyze_content_type(content, api_key, detection_provider)
                print(f"   ✅ AI detection: {', '.join(detected_types).upper()}")
            except Exception as e:
                print(f"   ⚠️ AI analysis failed ({e}), using heuristics")
                detected_types = heuristic_types
        else:
            detected_types = heuristic_types
            reason = "high confidence" if confidence >= 70 else "no API key"
            print(f"   ✅ Using heuristic result ({reason})")
        
        file_classifications[filename] = detected_types
        
        # 3. Distribute content to appropriate categories
        for dtype in detected_types:
            if dtype in categorized:
                if categorized[dtype]:
                    categorized[dtype] += f"\n\n--- FROM FILE: {filename} ---\n\n" + content
                else:
                    categorized[dtype] = content


    # 3. Context-Aware Gap Filling
    # If we have 2 files, and one is Q+R, the other is likely A (even if not detected)
    if len(files_content) == 2:
        filenames = list(files_content.keys())
        f1, f2 = filenames[0], filenames[1]
        types1 = file_classifications.get(f1, [])
        types2 = file_classifications.get(f2, [])
        
        # Scenario: File 1 is Question/Rubric, File 2 is unknown or just Question
        if ('question' in types1 or 'rubric' in types1) and 'answer' not in types1:
            if 'answer' not in types2:
                print(f"   💡 Context Inference: Assuming {f2} is the Student Answer")
                categorized['answer'] = files_content[f2]
                
        elif ('question' in types2 or 'rubric' in types2) and 'answer' not in types2:
            if 'answer' not in types1:
                print(f"   💡 Context Inference: Assuming {f1} is the Student Answer")
                categorized['answer'] = files_content[f1]

    # 4. Final Validation & Cleanup
    # If we have Question+Rubric in one bucket but missing the other, copy it over
    if categorized['question'] and not categorized['rubric']:
        # Double check if rubric keywords are in question text
        if any(kw in categorized['question'].lower() for kw in ['points', 'marks', 'grading']):
            print("   💡 Found potential rubric inside Question text, copying over.")
            categorized['rubric'] = categorized['question']
            
    # If we have Rubric but no Question, copy it over (often they are same file)
    if categorized['rubric'] and not categorized['question']:
         print("   💡 Found Rubric, assuming Question is also in there.")
         categorized['question'] = categorized['rubric']
            
    print("✅ Analysis Complete.\n")
    return categorized
