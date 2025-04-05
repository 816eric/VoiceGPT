
1. How to develop on R-PI
   1.1 Setup ssh to R-PI
   1.1.1 Check the IP Address cmd: ip addr
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
         Configure PuTTY to Use the Private Key:
            Open PuTTY and go to Connection > SSH > Auth.
            Under "Private key file for authentication", click "Browse" and select the id_rsa.ppk file you saved earlier.
            Go back to the Session category, enter the IP address of your Raspberry Pi, and save the session.
         Connect Using PuTTY:
            Open the saved session in PuTTY. You should now be able to log in without being prompted for a password.

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
      Add the following configuration to the config file:
        Host raspberrypi
        HostName <IP_ADDRESS>
        User pi
        IdentityFile C:/Users/<YourUsername>/.ssh/id_rsa
      Replace <IP_ADDRESS> with the IP address of your Raspberry Pi and <YourUsername> with your Windows username.
   
