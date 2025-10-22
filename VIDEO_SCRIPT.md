# Demo Video Script - Autonomous Ocean Forecasting Agent
## AWS AI Agent Global Hackathon 2025

**Duration:** 3 minutes  
**Format:** Screen recording + voiceover  
**Tools:** OBS Studio, Loom, or built-in screen recorder

---

## 🎬 Video Structure

### [0:00 - 0:30] HOOK & PROBLEM STATEMENT (30 seconds)

**Visual:** 
- Open with title slide: "Autonomous Ocean Forecasting Agent"
- Show news headlines about maritime accidents
- Display statistics on screen

**Script:**
> "Every year, the maritime industry—worth over $100 billion—loses millions of dollars due to accidents and operational inefficiencies caused by poor weather forecasting. Maritime operators struggle with fragmented data sources, complex analysis requirements, and delayed decision-making.
>
> But what if AI could autonomously monitor ocean conditions 24/7 and provide instant, actionable safety alerts?"

**On-Screen Text:**
- "$100B+ Maritime Industry"
- "Fragmented Data Sources"
- "Lives at Risk"

---

### [0:30 - 1:30] SOLUTION DEMONSTRATION (60 seconds)

**Visual:**
- Switch to live Streamlit interface
- Show agent in action

**Script:**
> "Introducing the Autonomous Ocean Forecasting Agent—powered by Amazon Bedrock AgentCore and Amazon Nova Pro.
>
> [Click to select Cape Town Harbor location]
> 
> Let me show you how it works. I'll query ocean conditions for Cape Town Harbor.
>
> [Click 'Analyze Ocean Conditions']
>
> Watch as the agent autonomously:
> 1. Fetches real-time ocean data from Copernicus Marine Service
> 2. Retrieves weather forecasts from Open-Meteo
> 3. Analyzes wave heights—here we see 3.2 meters with choppy seas
> 4. Evaluates current velocities at 2.4 kilometers per hour
> 5. And generates a color-coded alert
>
> [Point to results]
>
> The agent determines this is a CAUTION level situation—moderate waves with choppy seas. It provides specific recommendations: ensure all crew wear life jackets, maintain communication with shore, and monitor conditions continuously.
>
> Notice the clear severity indicators—red for dangerous, yellow for caution, green for safe—making it instantly readable for operators."

**Screen Highlights:**
- Hover over location selector
- Click analyze button
- Highlight wave height data
- Point to risk score (5/10)
- Show color-coded alert (🟡)
- Read recommendations

---

### [1:30 - 2:30] AUTONOMOUS CAPABILITIES & ARCHITECTURE (60 seconds)

**Visual:**
- Show architecture diagram
- Quick switch to different location
- Show agent adapting

**Script:**
> "What makes this truly powerful is its autonomous, multi-agent architecture.
>
> [Show architecture diagram]
>
> Built on Amazon Bedrock AgentCore Runtime with the Strands framework, our agent uses Amazon Nova Pro's reasoning capabilities to make intelligent decisions without human intervention.
>
> [Switch back to interface, select Singapore Strait]
>
> Let me demonstrate the autonomous capabilities—I'll now query Singapore Strait.
>
> [Click analyze]
>
> Watch how the agent adapts—same workflow, different location, completely autonomous. It retrieves location-specific data, analyzes unique conditions for this strait, and generates tailored recommendations.
>
> Behind the scenes, AWS Lambda fetches data, stores it in S3 for historical tracking, and the agent orchestrates multiple tools:
> - fetch_current_ocean_data
> - analyze_maritime_risks  
> - generate_forecast_alert
>
> All of this happens automatically, using chain-of-thought reasoning to ensure accurate risk assessment."

**Screen Actions:**
- Display architecture diagram for 10 seconds
- Return to app
- Select Singapore Strait (1.25, 103.85)
- Click analyze
- Show results
- Mention tool calls in console (if visible)

---

### [2:30 - 3:00] IMPACT & CALL TO ACTION (30 seconds)

**Visual:**
- Show impact metrics on screen
- End with project logo/title

**Script:**
> "The impact potential is enormous.
>
> This agent could prevent thousands of maritime accidents annually, reduce fuel costs by 20 to 30 percent through better route planning, and democratize access to ocean intelligence for small operators who can't afford expensive forecasting services.
>
> Built entirely on AWS serverless architecture—it's infinitely scalable, operating 24/7 with zero downtime.
>
> From fishing fleets to coast guard operations, from port authorities to recreational boaters—this AI agent is making the seas safer for everyone.
>
> Autonomous Ocean Forecasting Agent—building tomorrow's maritime safety solutions today."

**On-Screen Text:**
- "✅ Prevent Accidents"
- "✅ Reduce Costs 20-30%"
- "✅ 24/7 Autonomous Operation"
- "✅ Infinitely Scalable"
- "Built with: Amazon Bedrock AgentCore | Nova Pro | Strands"

**End Screen:**
```
Autonomous Ocean Forecasting Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AWS AI Agent Global Hackathon 2025

GitHub: [your-repo-url]
Live Demo: [your-demo-url]

Built with:
• Amazon Bedrock AgentCore
• Amazon Nova Pro
• Strands Agents Framework
• AWS Lambda | Amazon S3
```

---

## 🎥 Recording Tips

### Before Recording
- [ ] Close unnecessary browser tabs
- [ ] Disable notifications (Windows Focus Assist)
- [ ] Test microphone audio levels
- [ ] Rehearse script 2-3 times
- [ ] Have notes visible but off-screen
- [ ] Clear browser cache (fast loading)
- [ ] Ensure demo mode is enabled (if AWS not set up)

### During Recording
- [ ] Speak clearly and at moderate pace
- [ ] Pause briefly between sections
- [ ] Use mouse to highlight key elements
- [ ] Smile (it affects voice tone!)
- [ ] If you mess up, pause 3 seconds and restart sentence

### Recording Software Options

**Option 1: OBS Studio (Free, Professional)**
```
1. Download: https://obsproject.com/
2. Add Display Capture source
3. Add Audio Input Capture (microphone)
4. Settings → Output → Recording Quality: High
5. Start Recording → Record → Stop → Save
```

**Option 2: Loom (Easy, Web-Based)**
```
1. Visit: https://www.loom.com/
2. Install Chrome extension
3. Select "Screen + Camera" or "Screen Only"
4. Click Record
5. Download MP4 when done
```

**Option 3: Windows Game Bar (Built-in)**
```
1. Press Win + G
2. Click Record button
3. Press Win + Alt + R to stop
4. Videos saved to: Videos/Captures
```

**Option 4: PowerPoint (Combine Slides + Demo)**
```
1. Create slides for intro/stats/architecture
2. Use Slide Show → Record Slide Show
3. Switch to live demo during recording
4. Export as video
```

### After Recording
- [ ] Watch full video for errors
- [ ] Check audio is clear
- [ ] Verify text on screen is readable
- [ ] Trim any dead time at start/end
- [ ] Add captions if possible (YouTube auto-caption)
- [ ] Export at 1080p minimum
- [ ] File size under 500MB (if Devpost has limits)

### Video Editing (Optional)
- [ ] Add intro title (5 seconds)
- [ ] Add transitions between sections
- [ ] Highlight mouse cursor (optional)
- [ ] Add background music (low volume, royalty-free)
- [ ] Add text overlays for key points
- [ ] Add end screen with links

**Simple Editing Tools:**
- Windows: Built-in Video Editor
- Mac: iMovie
- Online: Kapwing.com (free)
- Advanced: DaVinci Resolve (free)

---

## 📤 Uploading Video

### YouTube (Recommended)
```
1. Go to: https://www.youtube.com/upload
2. Drag video file
3. Title: "Autonomous Ocean Forecasting Agent - AWS AI Agent Hackathon"
4. Description: [Include GitHub link, tech stack]
5. Visibility: "Unlisted" (or Public)
6. Copy video URL for Devpost
```

### Vimeo
```
1. Go to: https://vimeo.com/upload
2. Upload video
3. Set privacy to "Anyone"
4. Copy link for Devpost
```

### Direct Upload to Devpost
- Maximum file size varies (check during submission)
- MP4 format preferred
- H.264 codec recommended

---

## 🎯 Alternative Video Approaches

### If Short on Time

**Option A: Simple Screen Recording Only**
- Record screen with no voiceover
- Add text overlays explaining each step
- Use YouTube captions to add narration text
- Background music to fill silence

**Option B: Slide Deck + Screenshots**
- Create PowerPoint with screenshots
- Add speaker notes as captions
- Record slide show with audio
- Quick to produce, still effective

**Option C: Quick Demo with Points**
- 30s intro slide
- 2min straight demo recording
- 30s impact slide
- Less polish, but shows working solution

---

## ✅ Video Checklist

Before uploading:
- [ ] Duration: 2:30 - 3:30 (3 minutes target)
- [ ] Resolution: 1080p (1920x1080) minimum
- [ ] Format: MP4 or MOV
- [ ] Audio: Clear, no background noise
- [ ] Content: Shows end-to-end workflow
- [ ] Highlights: AWS services clearly mentioned
- [ ] Impact: Measurable benefits stated
- [ ] Professional: No errors or long pauses
- [ ] Accessible: Good audio and visuals
- [ ] Call-to-action: GitHub/demo links shown

---

## 🎬 Final Script Tips

1. **Energy:** Start strong, maintain enthusiasm
2. **Pace:** Speak slightly slower than normal conversation
3. **Clarity:** Emphasize key words (Amazon Bedrock AgentCore, autonomous, Nova Pro)
4. **Benefits:** Focus on "why it matters" not just "what it does"
5. **Demo:** Show don't tell—let the UI speak
6. **Confidence:** You built something amazing, show it!

---

**Ready to record? You've got this! 🎥🌊**

Remember: A working demo with clear explanation beats perfect production quality. Show your agent solving real problems, and the judges will be impressed.

Good luck! 🚀
