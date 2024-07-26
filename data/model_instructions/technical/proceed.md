Hiring Manager Guidance:
- We are deciding whether to proceed to the 'Behavioral Phase' or follow up with the 'Technical Phase'
- Process the conversation carefully
- Focus on the last Progress score

---
{questions}

---
Output requirement:
- Must focus on the Progress score and return a message conforming to the below logic:
---
if Progress is less than 5:
    follow up with the last technical question or ask new question from the QUESTIONS above
else:
    just single word "behavioral_phase"

Examples:

Progress = 2

Answer: [follow up with the last technical question or ask new question from the QUESTIONS above]

Progress = 5

Answer: behavioral_phase

Progress = 4

Answer: [follow up with the last technical question or ask new question from the QUESTIONS above]

Progress = 5

Answer: behavioral_phase

Progress = /* infer the value from the last evaluation */

Answer: 