# cloud-deallocator
(Work in progress) A python script to deallocate virtual machines in common cloud providers. At the moment only [Microsoft Azure](https://azure.microsoft.com/en-us/) is supported.

- [Supported Platforms](#supported-platforms)
- [Requirements](#requirements)
- [Installation](#installation)
- [Release History](#release-history)
- [Resources](#resources)


# Supported Platforms
Basically anything that has python.

# Requirements
- os: Likely any modern operating system that supports python.
    - What I used: Fedora Linux 35 (Workstation Edition)
- python: >= 3.10.3
    - What I used: 3.10.3
    - Packages: See [requirements.txt](requirements.txt)
- azure: 
    - You'll need a service principal with a role to permit reading and deallocating virtual machines.

# Installation
1. Install [python](https://www.python.org/)
    - If you don't have python installed, install from the above link. 
    - If you do have python installed check your version: ```python --version``` OR: ```python3 --version```
    - I used 3.10.3 so I would recommend that. Earlier python 3.x.x versions may also work but I can not guarantee it.
2. Create and activate a new virtual environment
    - Make sure python points to the appropriate python version before proceeding.
    - This will create a new virtual environment (See [docs](https://docs.python.org/3/library/venv.html) for more information)
        ```
        python -m venv cloud-deallocator-env
        ```
    - This will activate it (Assuming you're using linux)
        ```
        source cloud-deallocator-env/bin/activate
        ```
3. Install the required [pypi](https://pypi.org/) packages using [pip](https://pip.pypa.io/en/stable/)
    - Make sure the virtual environment is active first to avoid installing these globally.
    - This will install all the packages in the requirements.txt file
        ```
        pip install -r requirements.txt
        ```
4. Create a service principal and optionally define environment variables for development
    - Checkout [docs](https://docs.microsoft.com/en-us/azure/developer/python/configure-local-development-environment?tabs=cmd#configure-authentication) for guidance on configuring a service principal and environment variables.
    - Azure credentials can be imported from environment variables or a config.json file. See [set-env.sh.sample](scripts/set-env.sh.sample) for a list of sample environment variables.
5. Create a custom role for Azure
    - In order for the script to function it requires the following actions: 
        - "Microsoft.Compute/virtualMachines/read"
        - "Microsoft.Compute/virtualMachines/deallocate/action"
    - See [role_azure.json.sample](resources/roles/role_azure.json.sample) for a sample role.
    - Make sure you replace the sub-id with your own before using.
    - See [docs](https://docs.microsoft.com/en-us/azure/role-based-access-control/custom-roles) for guidance on how to create a custom role in Azure.
6. Add a role assignment for Azure
    - Apply the custom role you just created to a specific resource group or subscription
    - See [docs](https://docs.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal?tabs=current) for guidance on how to apply a role assignment in Azure.
7. Call the script
    - Make sure you have your virtual environment activated and config.json file populated or environment variables loaded
        - ```which python```: should point to your virtual environment
        - ```env | grep AZURE```: should show the required Azure environment variables if they're loaded (Linux only)
    - The following will execute the script if you're in the same directory as it
        - By default it will use environment variables. To use the config.json file uncomment azure_deallocator.deallocate_vms(config_source='json') and comment out azure_deallocator.deallocate_vms(config_source='env')
        ```
        python cloud_deallocator.py
        ```
8. See [resources](#resources) for additional information on things like: 
    - Scheduling the script via [crontab](https://man7.org/linux/man-pages/man5/crontab.5.html)
    - Creating a custom [alias](https://www.shell-tips.com/bash/alias/) to load your local dev environment
    - [Sourcing](https://linuxize.com/post/bash-source-command/) a shell script to load environment variables

# Release History
- 0.0.1 | 2022-04-01 | The "It works but only for Azure edition"
    - Basic script, very minor testing
    - Only support for Azure 

# Resources
### Example cron job
#### Description
Loads environment variables, python virtual environment and calls a python script every day at midnight
#### Instructions
**Please Note: The below instructions are documented for fedora linux.**

1. Copy below into a text editor and replace folder paths with your own:
    ```
    0 0 * * * source /home/$USER/Source/Envs/set-env.sh && source /home/$USER/Source/Envs/Python/venv/bin/activate && python $CLOUD_DEALLOCATOR_PATH/cloud_deallocator.py >> $CLOUD_DEALLOCATOR_PATH/bin/output.txt
    ```
    Above Explained:
    - 0 0 * * *
        - This is the cron schedule. The first 0 0 means at midnight and last * * * means every day of the month.
    - source /home/$USER/Source/Envs/set-env.sh
        - This calls a shell script to set all the environment variables used in proceeding commands and scripts. [Example](#example-shell-script-to-set-environment-variables)
    - source /home/$USER/Source/Envs/Python/venv/bin/activate
        - This activates a specified python virtual environment
    - python $CLOUD_DEALLOCATOR_PATH/cloud_deallocator.py >> $CLOUD_DEALLOCATOR_PATH/bin/output.txt
        - This calls the script and directs stdout to a text file in the project directory
2. Confirm cron is installed:
    ```
    rpm -q cronie
    ```
3. If it's not installed install it with:
    ```
    dnf install cronie
    ```
    If it is installed, ignore this step. Move on to step 5. If the status is not active, attempt step 4 first before proceeding.
4. Start crond service:
    ```
    systemctl start crond.service
    ```
5. Check crond service status:
    ```
    systemctl status crond.service
    ```
6. Open crontab editor for your current user and paste the cron entry:
    ```
    crontab -e 
    ```
7. Validate entry has been saved with: 
    ```
    crontab -l
    ```

### Example alias
#### Description
Load environment variables and python virtual environment. 
#### Instructions
**Please Note: The below instructions are documented for fedora linux.**
1. Copy below into a text editor and replace folder paths with your own:
    ```
    alias load-env="source ~/Source/Envs/set-env.sh && source ~/Source/Envs/Python/venv/bin/activate"
    ```
    For an explanation on these commands see: [Example](#example-cron-job)
2. Open .bashrc with a text editor and copy the alias:
    ```
    vi ~/.bashrc
    ```
    Open a new terminal window to load changes to .bashrc and validate everything is working after saving by typing the alias. 

### Example shell script to set environment variables
#### Description
Sets multiple environment variables referenced by the script/cron/alias
#### Instructions
**Please Note: The below instructions are documented for fedora linux.**
1. Copy below into a text editor and replace folder paths with your own:
    ```
    export AZURE_SUBSCRIPTION_ID="1234567890"
    export AZURE_TENANT_ID="1234567890"
    export AZURE_CLIENT_ID="1234567890"
    export AZURE_CLIENT_SECRET="1234567890"
    export AZURE_RESOURCE_GROUP_NAMES="Development, Production"
    export CLOUD_DEALLOCATOR_PATH="/home/$USER/Source/Repos/cloud-deallocator/"
    ```
    Above Explained:
    - export AZURE_SUBSCRIPTION_ID="1234567890"
    - export AZURE_TENANT_ID="1234567890"
    - export AZURE_CLIENT_ID="1234567890"
    - export AZURE_CLIENT_SECRET="1234567890"

        These are values needed by Azures Python SDK when using EnvironmentCredential as the credential source.

    - export AZURE_RESOURCE_GROUP_NAMES="Development, Production"

        This is a list of one or more resource groups to look for virtual machines in and is referenced in the script.

    - export CLOUD_DEALLOCATOR_PATH="/home/$USER/Source/Repos/cloud-deallocator/"

        This is the path to the repos used in the cron job.
2. Copy contents and save to a file called "set-env.sh" (Or rename the set-env.sh.sample file to set-env.sh and replace values with your own)
    ```
    vi set-env.sh
    ```
    Make sure the path to this file is updated in any cron jobs or alias' if also defining those based on the above examples.
