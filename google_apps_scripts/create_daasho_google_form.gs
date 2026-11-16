/**
 * Daasho Technologies Private Limited - BDE Recruitment Form Generator
 * Creates an official Google Form for Business Development Executive (Field Sales)
 * and links responses directly to Google Sheet:
 * https://docs.google.com/spreadsheets/d/1kxEeoG4dVSXgl5qfDTHGf3LlyEPgMQjrlAjvWFzzZ28/edit
 */

function createDaashoHiringForm() {
  var sheetId = "1kxEeoG4dVSXgl5qfDTHGf3LlyEPgMQjrlAjvWFzzZ28";

  // 1. Create Form
  var form = FormApp.create("Daasho - Business Development Executive (BDE) Application Form");
  form.setDescription(
    "Welcome to Daasho Technologies Careers (Everyday Delivery Platform in Chennai)!\n\n" +
    "Role: Business Development Executive (Field Sales)\n" +
    "Location: Chennai, Tamil Nadu\n" +
    "Experience: 0 - 3 Years (Freshers & Experienced Welcome)\n\n" +
    "Key Mandates:\n" +
    "• Fluent Tamil (Mandatory) + Basic English\n" +
    "• Passion for on-ground Field Sales & Merchant Onboarding\n" +
    "• Based in Chennai or anywhere in Tamil Nadu (Ready to relocate to Chennai)\n" +
    "• Two-wheeler with a valid driving license\n\n" +
    "Please fill in your details below. Shortlisted candidates will receive an interview call/WhatsApp within 24 hours."
  );
  
  form.setConfirmationMessage(
    "✅ Thank you for applying for the Business Development Executive (BDE) role at Daasho!\n\n" +
    "Our HR Recruitment Team will review your profile and contact you via Call / WhatsApp within 24 hours.\n" +
    "Direct HR Contact: Mr. Mohamed Yasar (+91 9025943184) | mohamed.yasar@daasho.com\n" +
    "Official Website: https://daasho.com"
  );
  form.setAllowResponseEdits(false);
  form.setProgressBar(true);

  // 2. Add Questions Tailored Strictly for BDE Role

  // Q1: Full Name
  form.addTextItem()
    .setTitle("1. Full Name")
    .setHelpText("Enter your official name as per Aadhaar / Government ID")
    .setRequired(true);

  // Q2: Mobile Number
  form.addTextItem()
    .setTitle("2. Mobile Number (WhatsApp Active)")
    .setHelpText("10-digit mobile number for interview calls and WhatsApp coordination")
    .setRequired(true);

  // Q3: Email Address
  form.addTextItem()
    .setTitle("3. Email Address")
    .setHelpText("Your primary email address for interview schedule and offer letter")
    .setRequired(true);

  // Q4: Current Location / District in Tamil Nadu
  form.addTextItem()
    .setTitle("4. Current Location / District")
    .setHelpText("e.g. Chennai (specify area), Coimbatore, Madurai, Trichy, Salem, Tirunelveli, etc.")
    .setRequired(true);

  // Q5: Ready to Relocate to Chennai
  form.addMultipleChoiceItem()
    .setTitle("5. Are you currently in Chennai, or ready to relocate to Chennai for this role?")
    .setHelpText("Daasho's BDE ground operations are based across Chennai")
    .setChoiceValues([
      "Yes, I am already residing in Chennai",
      "Yes, I am from Tamil Nadu and ready to relocate to Chennai immediately",
      "No, cannot relocate to Chennai"
    ])
    .setRequired(true);

  // Q6: Language Proficiency (Tamil is Mandatory)
  form.addMultipleChoiceItem()
    .setTitle("6. Are you fluent in Tamil? (Mandatory Requirement)")
    .setHelpText("Required for communicating and pitching to neighborhood merchant owners across Chennai")
    .setChoiceValues([
      "Yes, Fluent / Native Tamil Speaker (+ English / other languages)",
      "Yes, Fluent in Tamil only",
      "Basic Tamil",
      "No Tamil"
    ])
    .setRequired(true);

  // Q7: Total Work Experience (0 to 3 Years)
  form.addMultipleChoiceItem()
    .setTitle("7. Total Work Experience")
    .setHelpText("We welcome energetic freshers as well as experienced sales executives (0 - 3 Years)")
    .setChoiceValues([
      "Fresher (0 Years - Highly interested in field sales & fast learning)",
      "0 to 1 Year (Field Sales / Customer Facing / Retail)",
      "1 to 2 Years (BDE / Merchant Onboarding / FMCG / Delivery)",
      "2 to 3 Years (Experienced Sales Professional)",
      "3+ Years"
    ])
    .setRequired(true);

  // Q8: Field Sales Interest
  form.addMultipleChoiceItem()
    .setTitle("8. Do you have strong interest / experience in Field Sales?")
    .setHelpText("Visiting local restaurants, grocery stores & shops, pitching Daasho zero-commission model and onboarding them")
    .setChoiceValues([
      "Yes, I love field sales, meeting merchants and closing deals on-ground",
      "Yes, I am willing to learn and excited about field sales",
      "No, I am only looking for desk/office jobs"
    ])
    .setRequired(true);

  // Q9: Two-Wheeler & License
  form.addMultipleChoiceItem()
    .setTitle("9. Do you own a Two-Wheeler (Bike/Scooter) with a valid Driving License?")
    .setHelpText("Mandatory for daily field movement across assigned Chennai territories")
    .setChoiceValues([
      "Yes, I have a two-wheeler and a valid driving license",
      "I have a driving license; two-wheeler will be arranged before joining",
      "No"
    ])
    .setRequired(true);

  // Q10: Notice Period / Availability
  form.addMultipleChoiceItem()
    .setTitle("10. When can you join Daasho if selected?")
    .setChoiceValues([
      "Immediate Joiner (Within 1 - 2 Days)",
      "Within 7 Days",
      "Within 15 Days",
      "More than 15 Days"
    ])
    .setRequired(true);

  // Q11: Resume (Google Drive Link with public view access)
  form.addTextItem()
    .setTitle("11. Resume Link (Google Drive - Anyone with link can view)")
    .setHelpText("Upload resume to Google Drive -> Share -> Change General Access to 'Anyone with the link' (Viewer) -> Paste link here")
    .setRequired(false);

  // Q12: LinkedIn Profile URL (Separate field)
  form.addTextItem()
    .setTitle("12. LinkedIn Profile URL (Optional)")
    .setHelpText("Paste your LinkedIn profile URL (e.g. https://www.linkedin.com/in/your-profile)")
    .setRequired(false);

  // 3. Connect to the Google Sheet
  try {
    form.setDestination(FormApp.DestinationType.SPREADSHEET, sheetId);
    Logger.log("Successfully connected Form responses to Google Sheet: " + sheetId);
  } catch (e) {
    Logger.log("Notice on linking sheet destination: " + e);
  }

  // 4. Install Automated Email Trigger (Instant HR notification on every submission)
  try {
    var triggers = ScriptApp.getProjectTriggers();
    var triggerExists = triggers.some(function(t) {
      return t.getHandlerFunction() === "onCandidateFormSubmit";
    });
    if (!triggerExists) {
      ScriptApp.newTrigger("onCandidateFormSubmit")
        .forForm(form)
        .onFormSubmit()
        .create();
      Logger.log("Created automatic email alert trigger for new candidate applications.");
    }
  } catch (e) {
    Logger.log("Trigger setup note: " + e);
  }

  var publishedUrl = form.getPublishedUrl();
  var editUrl = form.getEditUrl();

  Logger.log("\n=======================================================");
  Logger.log("🎉 DAASHO BDE HIRING FORM READY!");
  Logger.log("🔗 Public Candidate Application URL: " + publishedUrl);
  Logger.log("✏️ Admin Edit Form URL:              " + editUrl);
  Logger.log("📊 Connected Google Sheet:           https://docs.google.com/spreadsheets/d/" + sheetId + "/edit");
  Logger.log("=======================================================\n");

  return {
    publishedUrl: publishedUrl,
    editUrl: editUrl
  };
}

/**
 * Automatically triggers when a candidate submits the application.
 * Sends instant email notification to Daasho HR.
 */
function onCandidateFormSubmit(e) {
  var itemResponses = e.response.getItemResponses();
  var candidate = {};
  for (var i = 0; i < itemResponses.length; i++) {
    candidate[itemResponses[i].getItem().getTitle()] = itemResponses[i].getResponse();
  }

  var hrEmail = "mohamed.yasar@daasho.com, mohammedyasar7868908@gmail.com";
  var candidateName = candidate["1. Full Name"] || "Candidate";
  var subject = "🚀 [Daasho BDE Application] " + candidateName + " - " + (candidate["4. Current Location / District"] || "Tamil Nadu");

  var body = 
    "Dear Daasho Recruitment Team,\n\n" +
    "A new candidate has submitted an application for the Business Development Executive (Field Sales) role!\n\n" +
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
    "📋 CANDIDATE SCREENING DETAILS\n" +
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
    "• Full Name:           " + candidate["1. Full Name"] + "\n" +
    "• Mobile (WhatsApp):   " + candidate["2. Mobile Number (WhatsApp Active)"] + "\n" +
    "• Email:               " + candidate["3. Email Address"] + "\n" +
    "• Current Location:    " + candidate["4. Current Location / District"] + "\n" +
    "• Relocation Ready:    " + candidate["5. Are you currently in Chennai, or ready to relocate to Chennai for this role?"] + "\n" +
    "• Tamil Fluency:       " + candidate["6. Are you fluent in Tamil? (Mandatory Requirement)"] + "\n" +
    "• Total Experience:    " + candidate["7. Total Work Experience"] + "\n" +
    "• Field Sales Passion: " + candidate["8. Do you have strong interest / experience in Field Sales?"] + "\n" +
    "• Bike & License:      " + candidate["9. Do you own a Two-Wheeler (Bike/Scooter) with a valid Driving License?"] + "\n" +
    "• Joining Period:      " + candidate["10. When can you join Daasho if selected?"] + "\n" +
    "• Resume (Drive Link): " + (candidate["11. Resume Link (Google Drive - Anyone with link can view)"] || "Not provided") + "\n" +
    "• LinkedIn Profile:    " + (candidate["12. LinkedIn Profile URL (Optional)"] || "Not provided") + "\n\n" +
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
    "📊 View Live Google Sheet with all responses:\n" +
    "https://docs.google.com/spreadsheets/d/1kxEeoG4dVSXgl5qfDTHGf3LlyEPgMQjrlAjvWFzzZ28/edit\n\n" +
    "— Daasho Recruitment Automation";

  MailApp.sendEmail(hrEmail, subject, body);
}
