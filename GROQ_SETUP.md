# GROQ SETUP GUIDE - Math Mentor AI
# Best free LLM for JEE-level math problems

## Step 1: Get Your Free API Key (1 minute)
1. Go to: https://console.groq.com
2. Sign up with Google/GitHub (free)
3. Click "API Keys" in left sidebar
4. Click "Create API Key"
5. Copy the key (starts with "gsk_...")

## Step 2: Add to .env file (30 seconds)
Open your .env file and add:

GROQ_API_KEY=gsk_your_key_here

## Step 3: Install Groq (30 seconds)
Run in terminal:
pip install groq

## Step 4: Test it! (30 seconds)
python check_groq.py

## DONE! Your Math Mentor now uses Groq's Llama 3.3 70B

---

## Why Groq for Math?

✅ Llama 3.3 70B - One of the smartest free models
✅ 500+ tokens/second - Super fast responses
✅ 14,400 requests/day free - Plenty for development
✅ Great at mathematical reasoning - Perfect for JEE problems

## Free Tier Limits

- 30 requests per minute
- 14,400 requests per day
- 7,000 requests per week

This means:
- 600+ math problems solved per day
- Perfect for testing and development
- Upgrade to paid if you need more (very cheap)

## Models Available on Groq

1. llama-3.3-70b-versatile (BEST for math) ⭐
2. llama-3.1-70b-versatile
3. mixtral-8x7b-32768
4. gemma2-9b-it

Your project is configured to use: llama-3.3-70b-versatile

---

## Comparison with Other Options

### Groq (Recommended) ⭐
- Speed: SUPER FAST (500+ tok/sec)
- Math ability: EXCELLENT (70B params)
- Free quota: HIGH (14,400/day)
- Setup: EASY (just API key)
**Best for: Production-ready math projects**

### Ollama (Alternative)
- Speed: SLOW (20-50 tok/sec)
- Math ability: GOOD (models up to 70B)
- Free quota: UNLIMITED
- Setup: MEDIUM (needs download)
**Best for: Privacy, offline work, unlimited usage**

### Gemini (Fallback)
- Speed: FAST
- Math ability: EXCELLENT
- Free quota: LIMITED (currently exceeded)
- Setup: EASY
**Best for: When Groq quota runs out**

---

## Your Project Now Supports ALL Three!

Priority order (automatic):
1. Try Groq first (fastest + best)
2. Fall back to Ollama if available
3. Fall back to Gemini if needed

This gives you maximum reliability!
