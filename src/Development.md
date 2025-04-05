
1. How to develop on R-PI
   1.1 Setup ssh to R-PI
      Enable SSH on Raspberry Pi:
         Open the terminal on your Raspberry Pi.
         Type sudo raspi-config and press Enter.
         Navigate to Interfacing Options and select SSH.
         Choose Enable and exit the configuration tool.
      Check the IP Address cmd: ip addr
      SSH from Another Device:
         Open the terminal on your computer (Windows, macOS, or Linux).
         Type ssh pi@<IP_ADDRESS> (replace <IP_ADDRESS> with the IP address of your Raspberry Pi).
         Press Enter and provide the password for your Raspberry Pi when prompted.
   1.2 Setup the key (PuTTY instead of ssh-agent - need admin right)
     Use PuTTY and PuTTYgen:  
        Generate SSH Key Pair:        
          Download PuTTYgen from the PuTTY website.
          Open PuTTYgen and click on the "Generate" button.
          Move your mouse around the blank area to generate randomness.
          Once the key is generated, save the private key (id_rsa.ppk) and the public key (id_rsa.pub).
              Save the public key by clicking "Save public key" in PuTTYgen. Name the file id_rsa.pub.
              Save the private key by clicking "Save private key". Name the file id_rsa.ppk.
        Copy the Public Key to Raspberry Pi:        
          Open PuTTY and connect to your Raspberry Pi using the IP address and your username.
          Once connected, run the following command to create the .ssh directory if it doesn't exist: mkdir -p ~/.ssh            
          Open the authorized_keys file in the .ssh directory: nano ~/.ssh/authorized_keys
          Copy the contents of the id_rsa.pub file from your local machine and paste it into the authorized_keys file on your Raspberry Pi.
          Save and exit the editor (Ctrl + X, then Y, then Enter).
         Set Permissions:
           chmod 700 ~/.ssh
           chmod 600 ~/.ssh/authorized_keys
         Check Ownership:
            chown -R pi:pi ~/.ssh
         Verify SSH Configuration on Raspberry Pi:         
            Open the SSH configuration file and ensure key-based authentication is enabled:
               sudo nano /etc/ssh/sshd_config         
            Ensure the following lines are present and not commented out:
               PubkeyAuthentication yes
               AuthorizedKeysFile .ssh/authorized_keys
         Save the file and restart the SSH service:
               sudo systemctl restart ssh

         Configure PuTTY to Use the Private Key:
            Open PuTTY and go to Connection > SSH > Auth.
            Under "Private key file for authentication", click "Browse" and select the id_rsa.ppk file you saved earlier.
            Go back to the Session category, enter the IP address of your Raspberry Pi, and save the session.
         Use Pageant (PuTTY Authentication Agent):
            Start Pageant (included with PuTTY) and load your private key:
               Open Pageant and right-click the icon in the system tray.
               Select "Add Key" and choose your id_rsa.ppk file.
            Enter the passphrase for your private key if prompted.
         Test the Connection:
            Open the saved session in PuTTY and try connecting again. Should connect to R-PI without a password.   

   1.3 Use VSCode to R-PI code
    Install VS Code and Remote-SSH Extension:
      Ensure you have VS Code installed on your computer. If not, download it from the VS Code website.
      Open VS Code and click on the Extensions icon on the left sidebar.
      Search for "Remote - SSH" and install the extension provided by Microsoft.
    Add SSH Host:    
      Open the Command Palette by pressing Ctrl + Shift + P.
      Type Remote-SSH: Open Configuration File and select it.
      Choose the SSH configuration file to edit. This is usually located at C:\Users\<YourUsername>\.ssh\config on Windows.
    Configure SSH Key:    
      Open your SSH config file located at %USERPROFILE%\\.ssh\\config (create the file if it does not exist). Add the following configuration to the config file:
        Host raspberrypi
           HostName <IP_ADDRESS>
           User pi
           IdentityFile C:/Users/<YourUsername>/.ssh/id_rsa
      Replace <IP_ADDRESS> with the IP address of your Raspberry Pi and <YourUsername> with your username.
   
