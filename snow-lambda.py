import json

def lambda_handler(event, context):
    try:
        # Parse body if API Gateway HTTP API (payload v2)
        payload = {}
        if isinstance(event, dict) and "body" in event:
            payload = json.loads(event["body"] or "{}")
        else:
            payload = event  # fallback if body already dict

        # Only use "Name" key
        first_name = payload.get("first_name", "unknown")
        last_name = payload.get("last_name", "unknown")
        email = payload.get("email", "unknown")
        username = payload.get("username", "unknown")
        job_title = payload.get("job_title", "unknown")
        department = payload.get("department", "unknown")
        manager_email = payload.get("manager_email", "unknown")
        location = payload.get("location", "unknown")

        print("ServiceNow payload details")
        print("Extracted First Name:", first_name)
        print("Extracted Last Name:", last_name)
        print("Extracted Email:", email)
        print("Extracted Username:", username)
        print("Extracted Job Title:", job_title)
        print("Extracted Department:", department)
        print("Extracted Manager's Email:", manager_email)
        print("Extracted Location:", location)
        
        
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
            "Success": True, 
            "First Name": first_name,
            "Last Name": last_name, 
            "Email": email,
            "Username": username, 
            "Job Title": job_title,
            "Department": department, 
            "Manager's Email": manager_email,
            "Location":location
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
