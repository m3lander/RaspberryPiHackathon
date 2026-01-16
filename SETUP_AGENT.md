# ElevenLabs Agent Setup Guide

This guide walks you through creating your Cash Recognition Agent in the ElevenLabs dashboard.

## Step 1: Create an Agent

1. Go to [ElevenLabs Conversational AI Agents](https://elevenlabs.io/app/conversational-ai/agents)
2. Click **"Create Agent"** or **"+ New Agent"**
3. Select **"Blank Template"**
4. Give it a name like "Cash Recognition Assistant"

## Step 2: Configure Basic Settings

### First Message
Set the agent's greeting:
```
Hey! I'm your assistant. I can identify banknotes or read text from packaging and labels. What would you like help with?
```

### System Prompt
This is critical - the prompt must tell the agent about its tools. Copy and paste:

```
You are a friendly assistant that helps visually impaired users. You have two tools:

1. "identify_cash" - Captures an image and identifies banknotes/currency
2. "read_packaging" - Captures an image and reads text from packaging, labels, or medication boxes

WHEN TO USE identify_cash:
- When the user asks about money, cash, banknotes, notes, or currency
- When the user asks "what am I holding?" and it's about money
- When the user wants to know the value of their money

WHEN TO USE read_packaging:
- When the user asks about ingredients, labels, or packaging
- When the user asks about medication, pills, or dosage
- When the user wants cooking instructions or preparation info
- When the user asks "what does this say?" about a box or package

AFTER IDENTIFYING CASH:
- State each note's denomination clearly (e.g., "twenty pounds")
- Mention the currency (e.g., "British Pound Sterling")
- If multiple notes, give the total

AFTER READING PACKAGING:
- Read the product name first
- For food: read ingredients, mention allergens, give cooking instructions
- For medication: emphasize drug name, dosage, and warnings
- Mention expiry dates if visible

HANDLING ISSUES:
- If nothing visible: suggest holding the item closer to the camera
- If image is blurry: "The image is unclear. Hold it still for a moment."
- If unsure: Be honest and describe what you can see

CONVERSATION STYLE:
- Keep responses brief and natural
- Be warm and patient
- Don't repeat yourself
```

### LLM Model
Choose: **Gemini 2.5 Flash** (or your preferred model)

## Step 3: Add the Client Tool

This is the most important step! The tool allows the agent to capture images.

1. In the agent settings, scroll to **"Tools"** section
2. Click **"+ Add Tool"**
3. Select **"Client Tool"** (NOT webhook!)

### Tool Configuration

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `identify_cash` |
| **Description** | `Captures an image from the camera and identifies any banknotes or currency visible. Call this tool when the user asks about money, cash, notes, or wants to know what currency they are holding.` |
| **Wait for response** | ✅ **CHECK THIS** |
| **Disable interruptions** | ✅ **CHECK THIS** |
| **Pre-tool speech** | Auto |
| **Execution mode** | Immediate |

### Parameters
Leave empty - no parameters needed:
- Don't click "Add param"
- The tool takes no input, it just captures from the camera

### Click "Add tool"

## Step 3b: Add the Packaging Reader Tool

Add a second client tool for reading packaging and labels.

1. Click **"+ Add Tool"** again
2. Select **"Client Tool"**

### Tool Configuration

| Field | Value |
|-------|-------|
| **Name** | `read_packaging` |
| **Description** | `Captures an image from the camera and reads text from packaging, labels, or medication boxes. Returns ingredients, cooking instructions, drug names and dosages, warnings, and other important information.` |
| **Wait for response** | ✅ **CHECK THIS** |
| **Disable interruptions** | ✅ **CHECK THIS** |
| **Pre-tool speech** | Auto |
| **Execution mode** | Immediate |

### Parameters
Leave empty - no parameters needed.

### Click "Add tool"

## Step 4: Voice Settings

1. Go to **"Voice"** settings tab
2. Choose a clear, natural voice:
   - **Rachel** - Clear and friendly
   - **Antoni** - Warm and conversational  
   - **Eric** - Professional
3. Recommended settings:
   - Model: **Eleven Turbo v2** (faster)
   - Stability: ~0.5
   - Similarity Boost: ~0.8

## Step 5: Save and Get Agent ID

1. Click **"Save"** at the top
2. Your **Agent ID** appears in the URL or agent details
3. It looks like: `agent_xxxxxxxxxxxx`
4. **Copy this ID** - you need it for your `.env` file

## Step 6: Test in Dashboard (Optional)

1. Click **"Test"** or **"Widget"** in the dashboard
2. Have a conversation
3. Say "What money am I holding?"
4. You should see the agent try to call `identify_cash`
5. (It won't work in the web test, but confirms the tool is configured)

## Step 7: Configure Your Pi

On your Raspberry Pi, edit the `.env` file:

```bash
nano ~/AccessibilityHackathon/.env
```

Add your credentials:
```
ELEVENLABS_API_KEY=sk_your_api_key_here
ELEVENLABS_AGENT_ID=agent_your_agent_id_here
GOOGLE_API_KEY=your_google_api_key_here
```

## Troubleshooting

### Agent says "I don't have access to tools"
1. Make sure you added **Client Tools** (not webhook)
2. Tool names must be exactly `identify_cash` and `read_packaging` (case-sensitive)
3. Update the System Prompt to explicitly mention both tools
4. Click **Save** after making changes

### Agent doesn't respond
1. Check your API key is valid
2. Check your Agent ID is correct
3. Try the agent in the ElevenLabs dashboard first

### Voice sounds robotic or slow
1. Use **Eleven Turbo v2** model for speed
2. Adjust stability/similarity settings
3. Try a different voice

### Agent talks too much
Add to system prompt:
```
Keep responses brief and to the point. One or two sentences is ideal.
```

---

## Quick Reference

| Tool | Name | Type | Wait for response |
|------|------|------|-------------------|
| Cash Recognition | `identify_cash` | Client Tool | ✅ Yes |
| Packaging Reader | `read_packaging` | Client Tool | ✅ Yes |

Both tools: Disable interruptions ✅, No parameters needed.

---

Once configured, run on your Pi:

```bash
cd ~/AccessibilityHackathon
source .venv/bin/activate
python main.py
```

Say **"Hey Pi"** then:
- **"What banknote am I holding?"** - to identify cash
- **"What does this label say?"** - to read packaging
- **"Read the ingredients"** - to read food packaging
- **"What medication is this?"** - to read pill boxes
