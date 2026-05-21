# ⚡ Quick Start Guide - HR Email Response Generator

Get up and running in 5 minutes!

---

## 🎯 Step 1: Install (2 minutes)

### Option A: Using pip
```bash
pip install -r requirements.txt
```

### Option B: Manual installation
```bash
pip install streamlit pandas anthropic
```

---

## 🔑 Step 2: Set API Key (1 minute)

### Option A: Environment Variable (Recommended)
```bash
# macOS/Linux
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxx"

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxx"
```

### Option B: .env File
Create a `.env` file in the same directory:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Get your API key:**
1. Go to https://console.anthropic.com/
2. Sign in with your account
3. Navigate to API Keys
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

---

## 📊 Step 3: Prepare Data (Already Done!)

The employee CSV file is already included:
```
/mnt/user-data/uploads/Employee_1000x.csv
```

This contains 1000 sample employees with names, emails, job titles, and contact info.

---

## 🚀 Step 4: Run the App (1 minute)

```bash
streamlit run hr_email_generator.py
```

The app will automatically open at:
```
http://localhost:8501
```

---

## 📧 Step 5: Generate Your First Email (1 minute)

### In the Streamlit App:

1. **Left Sidebar - Select Scenario**
   - Choose any HR scenario (e.g., "🎯 Joining Date Clarification")

2. **Left Sidebar - Select Employee**
   - Pick an employee from the dropdown

3. **Left Sidebar - Add Context**
   - Type what the employee's issue is:
     ```
     Employee is concerned about joining date delay,
     background check status is unclear, wants confirmation.
     ```

4. **Left Sidebar - Pick Tone**
   - Select: Empathetic, Formal, Supportive, or Action-Oriented

5. **Main Area - Click "Generate Email Response"**
   - Wait 2-3 seconds for the AI to draft the response

6. **Review the Email**
   - Read the generated response
   - Copy to clipboard or save to file

7. **Use the Email**
   - Copy to your email client
   - Customize any details
   - Send to the employee

---

## 💡 Pro Tips for Best Results

### ✅ What Works Well
- **Specific context**: Instead of "issue about joining", try "Background check pending since March 15, employee confused about start date"
- **Employee details matter**: The AI uses real job titles and names for personalization
- **Match the tone to your situation**: Formal for grievances, Supportive for onboarding issues
- **Regenerate if needed**: Each generation is unique, so try again if you don't like the first version

### ❌ Common Mistakes
- ❌ Not providing any context (generates generic response)
- ❌ Copying generated email without reviewing (always check!)
- ❌ Choosing formal tone for onboarding (supportive is better)
- ❌ Forgetting to add your name/title before sending

---

## 📋 Checklist for Each Email

Before sending any generated email:

- [ ] **Reviewed** - Read the entire email for quality
- [ ] **Verified Details** - Check dates, numbers, names are correct
- [ ] **Policy Aligned** - Ensure it follows company policies
- [ ] **Tone Appropriate** - Does it match the situation?
- [ ] **Legal Safe** - No overcommitments or false promises
- [ ] **Personalized** - Added your signature and contact info
- [ ] **Documented** - Saved a copy for records

---

## 🎓 10 Scenario Overview

| Icon | Scenario | Best For |
|------|----------|----------|
| 🎯 | Joining Date Clarification | New employee, background check delays |
| 🏖️ | Leave Policy Query | Leave balance questions |
| 🏢 | Work Arrangement | WFH/Hybrid/Office policy |
| ⚖️ | Grievance | Formal complaints (⚠️ Review with Legal!) |
| 📄 | Confirmation Letter | Delayed documentation |
| 🚚 | Relocation | Moving expenses, eligibility |
| 👶 | Parental Leave | Maternity, paternity, caregiver |
| 👋 | Exit Formalities | Resignations, exit process |
| 💰 | Payroll Concern | Salary, deductions, errors |
| 🚀 | Onboarding Escalation | New joiner support issues |

---

## 🔧 Troubleshooting

### Problem: "API Key not recognized"
**Solution:** 
```bash
# Verify your key is set
echo $ANTHROPIC_API_KEY

# Should show: sk-ant-xxxxx...
```

### Problem: "Module not found" error
**Solution:**
```bash
pip install streamlit pandas anthropic
```

### Problem: "CSV file not found"
**Solution:** Ensure the file path is correct:
```bash
ls -la /mnt/user-data/uploads/Employee_1000x.csv
```

### Problem: "Generated email too generic"
**Solution:** 
- Provide more specific context
- Be more detailed about the employee's situation
- Try a different tone option
- Click "Regenerate" for a different version

### Problem: "Streamlit not starting"
**Solution:**
```bash
# Kill any existing process
pkill -f streamlit

# Run again
streamlit run hr_email_generator.py
```

---

## 📱 Using on Different Platforms

### Windows
```batch
REM Set API key
set ANTHROPIC_API_KEY=sk-ant-xxxxx

REM Run app
streamlit run hr_email_generator.py
```

### macOS / Linux
```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# Run app
streamlit run hr_email_generator.py
```

---

## 💾 Exporting & Saving Emails

### Save to File
- Click "💾 Save Email" button
- File saved to: `/mnt/user-data/outputs/`
- Format: `HR_Email_YYYYMMDD_HHMMSS.txt`

### Copy to Clipboard
- Click "📋 Copy Email" button
- Paste into your email client
- Add your signature

### Keep Records
- Save all HR emails for compliance
- Document context and reasoning
- Maintain audit trail

---

## 🎯 Common Scenarios - Quick Templates

### "Employee asking about leave"
1. Scenario: **🏖️ Leave Policy**
2. Context: "Employee says their balance shows 8 days but they think they had 10"
3. Tone: **Supportive**

### "New person hasn't started yet"
1. Scenario: **🎯 Joining Date Clarification**
2. Context: "Background check pending, wants confirmation of start date"
3. Tone: **Empathetic**

### "Person is resigning"
1. Scenario: **👋 Exit Formalities**
2. Context: "Employee gave notice, confused about final paycheck and benefits"
3. Tone: **Supportive**

### "Salary error happened"
1. Scenario: **💰 Payroll Concern**
2. Context: "Employee reports they were charged extra tax this month"
3. Tone: **Action-Oriented**

---

## 🚨 Important Reminders

⚠️ **Always Review Before Sending**
- This tool helps draft, not replace human judgment
- Each situation is unique
- Your company's policies may differ
- When in doubt, consult Legal or your HR manager

⚠️ **Sensitive Issues**
- Grievances: Consult Legal before sending
- Terminations: Coordinate with Legal
- Discrimination claims: Escalate immediately
- Compliance issues: Verify with HR leadership

✅ **You Are in Control**
- Generated text is a starting point
- Feel free to edit and customize
- Add company-specific details
- Personalize with your voice and signature

---

## 📚 Need More Help?

- **Full Guide**: Read `README.md`
- **Sample Responses**: Check `SAMPLE_RESPONSES.md`
- **Code Comments**: See `hr_email_generator.py`
- **Streamlit Docs**: https://docs.streamlit.io
- **Claude API**: https://docs.anthropic.com

---

## ✨ You're Ready!

You now have everything needed to generate professional HR emails. 

**Next step:** Run the app and generate your first email! 🚀

```bash
streamlit run hr_email_generator.py
```

---

**Questions?** Refer to the full README.md or sample responses for more details.
