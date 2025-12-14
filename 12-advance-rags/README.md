# 12 - Advanced RAG Techniques

## What are Advanced RAG Techniques?

Beyond basic Retrieval-Augmented Generation, **advanced RAG techniques** improve retrieval quality and response accuracy through:

1. **Step-Back Prompting**: Abstract reasoning before specific retrieval
2. **Multi-Query**: Generate multiple query variations for better coverage
3. **Sub-Query**: Break complex queries into smaller retrievable parts

### Why Advanced RAG?

Basic RAG limitations:
- **Single Query**: May miss relevant documents
- **Literal Matching**: Doesn't handle paraphrasing well
- **Complex Questions**: Hard to retrieve for multi-part queries

Advanced techniques solve these problems.

---

## Implemented Techniques

### 1. **Step-Back Prompting**

**Concept**: Generate a higher-level, more abstract question before retrieval.

**How it works**:
```
Original Query: "How do I fix a memory leak in my React component?"

Step-Back Query: "What are common memory management issues in React?"

Retrieval: Search for both queries
- Original finds specific fixes
- Step-back finds broader context

Combined Result: Better understanding + specific solution
```

**Benefits**:
- Provides conceptual context
- Finds related broader topics
- Improves reasoning quality
- Reduces over-specificity

**Example**:
```python
original_query = "How to configure SSL in nginx v1.20?"

# Generate step-back query
step_back_query = llm.generate(
    "Given the question: {original_query}, "
    "generate a more general question about the underlying concept."
)
# → "How does SSL/TLS work in web servers?"

# Retrieve for both queries
general_docs = retrieve(step_back_query)
specific_docs = retrieve(original_query)

# Combine context
combined_context = general_docs + specific_docs
```

---

### 2. **Multi-Query**

**Concept**: Generate multiple variations of the same question to improve recall.

**How it works**:
```
Original Query: "What is machine learning?"

Generated Queries:
1. "Define machine learning"
2. "Explain what ML is"
3. "How does machine learning work?"
4. "Introduction to machine learning concepts"

Retrieval: Search with all queries
Result: Union of all retrieved documents
```

**Benefits**:
- Handles different phrasings
- Captures multiple perspectives
- Improves document recall
- Reduces query bias

**Example**:
```python
original_query = "Python async programming best practices"

# Generate query variations
variations = llm.generate(
    "Generate 3 alternative ways to ask: {original_query}"
)
# → [
#     "How to write asynchronous code in Python effectively",
#     "Best patterns for Python asyncio development",
#     "Python concurrency best practices"
# ]

# Retrieve for all variations
all_docs = []
for query in [original_query] + variations:
    docs = vector_db.search(query)
    all_docs.extend(docs)

# Deduplicate and rank
unique_docs = deduplicate(all_docs)
```

---

### 3. **Sub-Query**

**Concept**: Decompose complex questions into simpler sub-questions.

**How it works**:
```
Complex Query: "Compare Python and JavaScript for web development, 
                including performance, ecosystem, and learning curve"

Sub-Queries:
1. "Python performance in web development"
2. "JavaScript performance in web development"
3. "Python web development ecosystem"
4. "JavaScript web development ecosystem"
5. "Learning curve for Python"
6. "Learning curve for JavaScript"

Retrieval: Search each sub-query independently
Result: Comprehensive answer synthesized from all parts
```

**Benefits**:
- Handles multi-part questions
- Structured information gathering
- Better coverage of complex topics
- Clearer reasoning path

**Example**:
```python
complex_query = """
What are the differences between React, Vue, and Angular in terms of:
- Performance
- Learning curve
- Community support
- Use cases
"""

# Generate sub-queries
sub_queries = llm.generate(
    "Break down this complex question into simpler sub-questions: {complex_query}"
)
# → [
#     "React framework performance characteristics",
#     "Vue.js framework performance characteristics",
#     "Angular framework performance characteristics",
#     "React learning curve difficulty",
#     "Vue.js learning curve difficulty",
#     ...
# ]

# Retrieve for each sub-query
sub_answers = {}
for sub_q in sub_queries:
    docs = vector_db.search(sub_q)
    answer = llm.answer(sub_q, docs)
    sub_answers[sub_q] = answer

# Synthesize final answer
final_answer = llm.synthesize(
    original_query=complex_query,
    sub_answers=sub_answers
)
```

---

## Comparison Table

| Technique | Use Case | Pros | Cons |
|-----------|----------|------|------|
| **Step-Back** | Need conceptual understanding | Broader context | Extra LLM call |
| **Multi-Query** | Handle paraphrasing | Better recall | More retrievals |
| **Sub-Query** | Complex multi-part questions | Comprehensive | Slower, more expensive |

---

## Combined Workflow Example

```python
def advanced_rag(query: str):
    """
    Combined advanced RAG pipeline.
    """
    # 1. Step-Back: Get conceptual context
    step_back_query = generate_step_back(query)
    general_docs = retrieve(step_back_query)
    
    # 2. Multi-Query: Generate variations
    query_variations = generate_variations(query)
    
    # 3. Sub-Query: Decompose if complex
    if is_complex(query):
        sub_queries = decompose(query)
        all_docs = []
        
        for sub_q in sub_queries:
            # Apply multi-query to each sub-query
            sub_variations = generate_variations(sub_q)
            for variation in sub_variations:
                docs = retrieve(variation)
                all_docs.extend(docs)
    else:
        # Simple query: just multi-query
        all_docs = []
        for variation in query_variations:
            docs = retrieve(variation)
            all_docs.extend(docs)
    
    # 4. Combine all documents
    combined_docs = deduplicate(general_docs + all_docs)
    
    # 5. Rank by relevance
    ranked_docs = rerank(combined_docs, query)
    
    # 6. Generate final answer
    answer = llm.generate(query, ranked_docs)
    
    return answer
```

---

## Implementation Notes

This folder contains **foundational code** for advanced RAG techniques. The `main.py` file is a placeholder for implementing:

### Step-Back Implementation:
```python
def step_back_prompting(query: str):
    # Generate abstract question
    step_back_prompt = f"""
    Given the specific question: {query}
    Generate a more general question about the underlying concept.
    """
    general_query = llm.generate(step_back_prompt)
    
    # Retrieve both
    specific_docs = vector_db.search(query)
    general_docs = vector_db.search(general_query)
    
    return specific_docs + general_docs
```

### Multi-Query Implementation:
```python
def multi_query_retrieval(query: str):
    # Generate variations
    variations_prompt = f"""
    Generate 3 different ways to ask this question: {query}
    Provide variations that capture different aspects.
    """
    variations = llm.generate(variations_prompt)
    
    # Retrieve for all
    all_docs = []
    for var in variations:
        docs = vector_db.search(var)
        all_docs.extend(docs)
    
    # Deduplicate
    unique_docs = list(set(all_docs))
    return unique_docs
```

### Sub-Query Implementation:
```python
def sub_query_decomposition(complex_query: str):
    # Decompose into sub-queries
    decompose_prompt = f"""
    Break down this complex question into simpler sub-questions:
    {complex_query}
    
    Each sub-question should be independently answerable.
    """
    sub_queries = llm.generate(decompose_prompt)
    
    # Answer each sub-query
    sub_answers = {}
    for sub_q in sub_queries:
        docs = vector_db.search(sub_q)
        answer = llm.answer(sub_q, docs)
        sub_answers[sub_q] = answer
    
    # Synthesize final answer
    synthesis_prompt = f"""
    Original question: {complex_query}
    
    Sub-answers:
    {format_sub_answers(sub_answers)}
    
    Synthesize a comprehensive answer to the original question.
    """
    final_answer = llm.generate(synthesis_prompt)
    return final_answer
```

---

## When to Use Each Technique

### Step-Back Prompting:
- ✅ Educational queries
- ✅ Need conceptual understanding
- ✅ Technical documentation
- ❌ Simple fact lookup

### Multi-Query:
- ✅ Natural language queries
- ✅ Ambiguous questions
- ✅ Improve recall
- ❌ When query is already precise

### Sub-Query:
- ✅ Complex, multi-part questions
- ✅ Comparison queries
- ✅ Analytical questions
- ❌ Simple, single-answer questions

---

## Use Cases

1. **Technical Documentation Search**:
   - Step-back: Understand concepts
   - Multi-query: Handle different terminology
   - Sub-query: Compare solutions

2. **Research Assistants**:
   - Step-back: Background context
   - Sub-query: Break down research questions

3. **Customer Support**:
   - Multi-query: Handle user paraphrasing
   - Sub-query: Complex troubleshooting

4. **Educational Platforms**:
   - Step-back: Build foundational knowledge
   - Sub-query: Structured learning paths

---

## Performance Considerations

| Aspect | Impact | Mitigation |
|--------|--------|------------|
| **Latency** | 2-3x slower | Cache queries, parallel retrieval |
| **Cost** | More LLM calls | Batch processing, use cheaper models |
| **Complexity** | Harder to debug | Log all steps, add monitoring |
| **Accuracy** | Higher | Worth the tradeoff for critical apps |

---

## Key Takeaways

- Advanced RAG improves retrieval quality
- **Step-back**: Adds conceptual context
- **Multi-query**: Handles paraphrasing
- **Sub-query**: Tackles complex questions
- Combine techniques for best results
- Tradeoff: Accuracy vs. Speed/Cost
- Essential for production RAG systems
- Foundation for intelligent retrieval

---

## Next Steps

- **13-voice-agents**: Voice-based AI interactions
- Implement hybrid retrieval (keyword + semantic)
- Add reranking for better document selection
- Experiment with query expansion techniques
