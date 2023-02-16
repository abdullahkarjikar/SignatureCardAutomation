import pandas as pd

#df = pd.read_csv('/Users/abdullakarjikar/Downloads/FormSubmissions.csv')
#df.drop(df.columns[[6, 9, 10, 17]], axis = 1, inplace = True)
sigCardCols = ["SubmissionId", "DateSubmitted", "Username", "First Name", "Last Name", "Status", "Comment", "Updated By", "Updated On", "Revisor", 
               "InstructionFirstIgnore", "Full Organization name" ,"Treasurer OSU email", "Presidents OSU email", "Advisors OSU email", 
               "Co-Advisors OSU email", "Additional Co-Advisors OSU email", "InstructionSecondIgnore"]

dirCols = ["Organization ID", "Organization Name", "Short Name", "Organization Type", "Status", "Website", "Website Key", "Organization Email", 
           "Address Line 1", "Address Line 2", "City", "State", "ZIP", "Phone Number", "Fax Number", "Parent Organization", "Approved Service Hours", 
           "Current Member Count", "Past Member Count", "Primary Contact", "Primary Contact Campus Email", "Primary Contact Preferred Email", 
           "Primary Contact Local Phone", "Primary Contact Mobile Phone", "Categories", "01. Status", "02. Advisor", "03. Adv Department", 
           "04. Adv Address", "05. Adv Email", "06. Adv Phone", "08. President:", "10. Pres Email", "11. Pres Phone", "12. Vice President", "14. VP Email", 
           "15. VP Phone", "16. Treasurer", "18. Treas Email", "19. Treas Phone", "20. Secretary", "22. Sec Email", "23. Sec Phone", "24. Co-Advisor(s)", 
           "25. Co-Advisor(s) Address", "26. Co-Advisor(s) Email", "27. Co-Advisor(s) Phone", "29. Administrator-Only Notes", 
           "30. Fund Code (Account Number) and Organization Code", "Constitution Updated on (MM/DD/YYYY):", 
           "If organization has been declared inactive,provide date occurred & reason. DO NOT DELETE", "When is your NEXT election?", 
           "1.1 Sponsoring Organization/Department"]

df_SignatureCards = pd.read_csv("/Users/abdullakarjikar/Downloads/FormSubmissions__.csv", skiprows=3, names=sigCardCols)
df_Directory = pd.read_csv("/Users/abdullakarjikar/Downloads/OrganizationDirectory__.csv", skiprows=3, names=dirCols)

#print(df.columns)
#$print(df.head())
signature_Card_Pending = df_SignatureCards[df_SignatureCards["Status"] == "Pending"]
signatureCards = signature_Card_Pending[["Full Organization name", "Treasurer OSU email", "Presidents OSU email", "Advisors OSU email", 
               "Co-Advisors OSU email", "Additional Co-Advisors OSU email"]]

print(signatureCards.columns)

#print(signature_Card_Pending)
for ind, each in signatureCards.iterrows():
    print(type(each))
    #print(each["Status"], each["First Name"], each["Last Name"], each["Full Organization name"])




#df_modified = df[1:]
#
#print(df_modified.columns)
#print(df['Status'])
# df_Status = df.query("Status == 'Pending'")
# print(df_Status.count())

