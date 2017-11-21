def determine_action(action_name):
    action_name = action_name.lower()

    if action_name == "logging in":
        return "has logged in"
    if action_name == "logging out":
        return "has logged out"
    if action_name == "create appointment":
        return "has created an appointment"
    if action_name == "update appointment":
        return "has updated an appointment"
    if action_name == "delete appointment":
        return "has deleted an appointment"
    if action_name == "create user":
        return "has created a new user"
    if action_name == "update profile info":
        return "has updated their profile information"
    if action_name == "register":
        return "has registered"
    if action_name == "change password":
        return "has changed their password"