/**
 * Daasho Technologies - Candidate Application Form Generator
 * Creates a professional Google Form and links all responses directly to Google Sheet:
 * https://docs.google.com/spreadsheets/d/1kxEeoG4dVSXgl5qfDTHGf3LlyEPgMQjrlAjvWFzzZ28/edit
 */

function createDaashoHiringForm() {
  var sheetId = "1kxEeoG4dVSXgl5qfDTHGf3LlyEPgMQjrlAjvWFzzZ28";

  // 1. Create Form
  var form = FormApp.create("Daasho - Official Candidate Job Application Form");
  form.setDescription(
    "Welcome to Daasho Technologies Private Limited Careers.\n\n" +
    "We are hiring Business Development Executives (Field Sales) & HR Operations team in Chennai.\n" +
    "Please fill in your details accurately. Shortlisted candidates will be contacted via WhatsApp/Call for immediate interviews."
  );
  form.setConfirmationMessage(
    "✅ Thank you for applying to Daasho!\n\n" +
    "Our HR Recruitment Team will review your application and contact you via WhatsApp / Call within 24 hours.\n" +
    "Fast-track review contact: +91 9787806366"
  );
  form.setAllowResponseEdits(false);
  form.setProgressBar(true);

  // 2. Add Questions
  // Q1: Full Name
  form.addTextItem()
    .setTitle("1. Full Name")
    .setHelpText("Enter your legal name as per government ID")
    .setRequired(true);

  // Q2: Mobile Number
  form.addTextItem()
    .setTitle("2. Mobile Number (WhatsApp Active)")
    .setHelpText("Active 10-digit number for interview scheduling & WhatsApp updates")
    .setRequired(true);

  // Q3: Email Address
  form.addTextItem()
    .setTitle("3. Email Address")
    .setHelpText("Your primary email for offer letter & interview call letter")
    .setRequired(true);

  // Q4: Role Applying For
  form.addMultipleChoiceItem()
    .setTitle("4. Position You Are Applying For")
    .setChoiceValues([
      "Business Development Executive (Field Sales - Chennai)",
      "Field Sales Executive (Merchant Onboarding)",
      "HR Executive / Recruiter",
      "Delivery Operations & Fleet Supervisor"
    ])
    .setRequired(true);

  // Q5: Location / Area in Chennai
  form.addTextItem()
    .setTitle("5. Current Location / Area in Chennai")
    .setHelpText("e.g. Guindy, Alwarpet, Velachery, Anna Nagar, Tambaram, etc.")
    .setRequired(true);

  // Q6: Total Sales / Work Experience
  form.addMultipleChoiceItem()
    .setTitle("6. Total Work Experience")
    .setChoiceValues([
      "Fresher (Excited to learn & earn high incentives)",
      "6 Months - 1 Year",
      "1 - 2 Years",
      "2 - 3 Years",
      "3+ Years"
    ])
    .setRequired(true);

  // Q7: Two-Wheeler & License
  form.addMultipleChoiceItem()
    .setTitle("7. Do you have a Two-Wheeler (Bike/Scooter) with a valid Driving License?")
    .setHelpText("Required for Field Sales & Merchant visits across Chennai")
    .setChoiceValues([
      "Yes, I have a two-wheeler and valid driving license",
      "I have a driving license, bike will be arranged soon",
      "No"
    ])
    .setRequired(true);

  // Q8: Joining Time
  form.addMultipleChoiceItem()
    .setTitle("8. How soon can you join if selected?")
    .setChoiceValues([
      "Immediate Joiner (Today / Tomorrow)",
      "Within 3 - 5 Days",
      "1 Week",
      "15 Days"
    ])
    .setRequired(true);

  // Q9: Resume or LinkedIn Profile
  form.addTextItem()
    .setTitle("9. Resume Link (Google Drive) or LinkedIn Profile URL")
    .setHelpText("Paste your LinkedIn profile link or public Google Drive link to your resume")
    .setRequired(false);

  // 3. Connect to the Google Sheet
  try {
    form.setDestination(FormApp.DestinationType.SPREADSHEET, sheetId);
    Logger.log("Successfully connected Form responses to Google Sheet: " + sheetId);
  } catch (e) {
    Logger.log("Notice on linking sheet destination: " + e);
  }

  var publishedUrl = form.getPublishedUrl();
  var editUrl = form.getEditUrl();

  Logger.log("\n=======================================================");
  Logger.log("🎉 DAASHO HIRING FORM READY!");
  Logger.log("🔗 Public Candidate Application URL: " + publishedUrl);
  Logger.log("✏️ Admin Edit Form URL:              " + editUrl);
  Logger.log("📊 Connected Google Sheet:           https://docs.google.com/spreadsheets/d/" + sheetId + "/edit");
  Logger.log("=======================================================\n");

  return {
    publishedUrl: publishedUrl,
    editUrl: editUrl
  };
}
