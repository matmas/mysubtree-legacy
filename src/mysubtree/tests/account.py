# -*- coding: utf-8 -*-
from .base import Base

class Account(Base):
    def runTest(self):
        email="test@example.com"
        name=u"Testerľ"
        password=u"TestersPasswordľ"
        
        # Try register with wrong e-mail:
        data = dict(email="wrong e-mail", name=name, password=password, password_again=password)
        rv = self.client.post("/en/create-account", data=data, follow_redirects=True)
        assert "Invalid e-mail address." in rv.data
        
        # Try register with too short name:
        data = dict(email=email, name="A", password=password, password_again=password)
        rv = self.client.post("/en/create-account", data=data, follow_redirects=True)
        assert "Field must be at least 2 characters long." in rv.data
        
        # Create account:
        rv = self.create_account(email, name, password)
        verification_link = self.get_verification_link(rv.data)
        
        # Try to create account with the same e-mail:
        rv = self.create_account(email, name, password)
        assert "Such e-mail address is just in process of being registered." in rv.data
        
        # Try to login without verified e-mail:
        rv = self.login(email, password)
        assert "The e-mail address is not yet verified." in rv.data
        
        # Verify e-mail:
        rv = self.client.get(verification_link, follow_redirects=True)
        assert "E-mail was successfully verified." in rv.data
        
        # Verify e-mail again:
        rv = self.client.get(verification_link, follow_redirects=True)
        assert "E-mail is already verified." in rv.data
        
        # Verify whong code:
        rv = self.client.get("/en/verify/INVALID_CODE", follow_redirects=True)
        assert "Invalid verification code." in rv.data
        
        # Login:
        rv = self.login(email=email, password=password)
        assert "You have been logged in." in rv.data
        
        # Logout:
        rv = self.logout()
        assert "You have been logged out." in rv.data
        
        # Try wrong password:
        rv = self.login(email=email, password="wrong password")
        assert "The password you provided is incorrect." in rv.data
        
        # Try wrong e-mail:
        rv = self.login(email="wrong e-mail", password=password)
        assert "The e-mail you provided is not registered." in rv.data
        
        # Password reset:
        rv = self.client.get("/en/forgot")
        rv = self.client.post("/en/forgot")
        assert "Form did not have all fields filled correctly." in rv.data
        
        # Request password reset with unregistered e-mail:
        rv = self.client.post("/en/forgot", data=dict(email="unknown@example.com"), follow_redirects=True)
        assert "The e-mail you provided is not registered." in rv.data
        
        # Request password reset:
        rv = self.client.post("/en/forgot", data=dict(email="test@example.com"), follow_redirects=True)
        message = "Use the following link within 24 hours to reset your password:"
        assert message in rv.data
        i = rv.data.find(message) + len(message)
        reset_link = rv.data[i:rv.data.find("<", i)].strip()
        reset_link = reset_link[len("http://localhost"):]
        assert reset_link.startswith("/en/reset/")
        assert len(reset_link) == len("/en/reset/") + 10
        
        # Request password reset second time:
        rv = self.client.post("/en/forgot", data=dict(email="test@example.com"), follow_redirects=True)
        assert "The e-mail has already been sent." in rv.data
        
        # Set new password:
        rv = self.client.post(reset_link, data=dict(password="new password", password_again="new password"), follow_redirects=True)
        assert "Password changed successfully." in rv.data
        
        # Try old password:
        rv = self.login(email=email, password=password)
        assert "The password you provided is incorrect." in rv.data
        
        # Try new password:
        rv = self.login(email=email, password="new password")
        assert "You have been logged in." in rv.data
        
        # Try register again with the same e-mail
        rv = self.create_account(email, name, password)
        assert "Such e-mail address is already registered." in rv.data
