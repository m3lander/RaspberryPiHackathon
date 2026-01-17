# ElevenLabs Agent Setup Guide

This guide walks you through creating your eBay Item Recognition Agent in the ElevenLabs dashboard.

## Step 1: Create an Agent

1. Go to [ElevenLabs Conversational AI Agents](https://elevenlabs.io/app/conversational-ai/agents)
2. Click **"Create Agent"** or **"+ New Agent"**
3. Select **"Blank Template"**
4. Give it a name like "eBay Listing Assistant"

## Step 2: Configure Basic Settings

### First Message
Set the agent's greeting:
```
Hey! I'm your eBay listing assistant. Hold up an item to the camera and I'll describe it for you - including brand, size, color, and condition.
```

### System Prompt
This is critical - the prompt must tell the agent about its tools. Copy and paste:

```
You are a friendly assistant that helps visually impaired eBay sellers create item listings. You have two tools:

1. "identify_item" - Captures an image and identifies e-commerce item details for eBay listings
2. "read_packaging" - Captures an image and reads text from clothing tags, care labels, or product packaging

WHEN TO USE identify_item:
- When the user asks "What is this item?" or "Describe this"
- When the user wants to list something on eBay
- When the user asks about brand, size, color, or condition
- When the user shows you clothing, electronics, accessories, or any sellable item
- When the user asks "What am I holding?"

WHEN TO USE read_packaging:
- When the user specifically asks to "read the tag" or "read the label"
- When the user asks about size tags or care instructions
- When the user wants material composition or washing instructions
- When the user asks "What does this say?" about a tag or label

AFTER IDENTIFYING AN ITEM, include:
- Item type (e.g., "men's jacket", "smartphone")
- Brand name if visible
- Size (S/M/L, numeric, or dimensions)
- Colors (primary and secondary)
- Condition (New with tags, Like new, Good, Fair, Poor)
- Any visible defects (stains, tears, scratches, missing parts)
- Material if identifiable
- Special features (pockets, patterns, hardware)

AFTER READING A TAG/LABEL:
- Read the brand name
- Read the size
- Read material composition
- Mention care instructions
- Note country of manufacture if visible

HANDLING ISSUES:
- If the image is blurry: "The image is unclear. Please hold the item still."
- If you can't see the item clearly: "Please hold the item closer to the camera."
- If details are unclear: Be honest about what you cannot determine.

CONVERSATION STYLE:
- Keep responses conversational but thorough
- Describe items as you would to someone who cannot see them
- Be specific about defects - eBay buyers appreciate honesty
- Don't repeat information unnecessarily
```

### LLM Model
Choose: **Gemini 2.5 Flash** (or your preferred model)

## Step 3: Add the Item Recognition Tool

This is the most important step! The tool allows the agent to capture and analyze items.

1. In the agent settings, scroll to **"Tools"** section
2. Click **"+ Add Tool"**
3. Select **"Client Tool"** (NOT webhook!)

### Tool Configuration

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `identify_item` |
| **Description** | `Captures an image and identifies item details for eBay listings including brand, size, color, condition, and defects. Call this tool when the user wants to describe or list an item.` |
| **Wait for response** | Yes |
| **Disable interruptions** | Yes |
| **Pre-tool speech** | Auto |
| **Execution mode** | Immediate |

### Parameters
Leave empty - no parameters needed:
- Don't click "Add param"
- The tool takes no input, it just captures from the camera

### Click "Add tool"

## Step 3b: Add the Packaging/Label Reader Tool

Add a second client tool for reading clothing tags and labels.

1. Click **"+ Add Tool"** again
2. Select **"Client Tool"**

### Tool Configuration

| Field | Value |
|-------|-------|
| **Name** | `read_packaging` |
| **Description** | `Captures an image and reads text from clothing tags, care labels, or product packaging. Returns brand, size, material composition, care instructions, and other label information.` |
| **Wait for response** | Yes |
| **Disable interruptions** | Yes |
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
3. Say "What item is this?"
4. You should see the agent try to call `identify_item`
5. (It won't work in the web test, but confirms the tool is configured)

## Step 7: Configure Your Pi

On your Raspberry Pi, edit the `.env` file:

```bash
nano ~/RaspberryPiHackathon/.env
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
2. Tool names must be exactly `identify_item` and `read_packaging` (case-sensitive)
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
Keep responses concise. Focus on the key details: brand, size, color, condition, and defects.
```

---

## Quick Reference

| Tool | Name | Type | Wait for response |
|------|------|------|-------------------|
| Item Recognition | `identify_item` | Client Tool | Yes |
| Tag/Label Reader | `read_packaging` | Client Tool | Yes |

Both tools: Disable interruptions Yes, No parameters needed.

---

## Example Voice Commands

Once configured, run on your Pi:

```bash
cd ~/RaspberryPiHackathon
source .venv/bin/activate
python main.py
```

Say **"Hey Pi"** then:
- **"What is this item?"** - to identify any item
- **"Describe this for eBay"** - to get a full listing description
- **"What brand is this?"** - to identify brand
- **"What size is this?"** - to check size
- **"What condition is it in?"** - to assess condition
- **"Are there any defects?"** - to check for wear/damage
- **"Read the size tag"** - to read clothing labels
- **"What does the label say?"** - to read product tags
