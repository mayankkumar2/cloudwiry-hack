# Cloudwiry Hack Sumission

This hack presents my idea for a scalable key-blob storage system. The interface for the service is using a CLI application. The hack uses ZStandard compression to save storage space on the servers. The hack employs message queues to remove dangling files on the server once a user requests a deletion. The hack also supports versioning of data, so all your files saved on the server are securely stored and you can randomly reference any version of it.

[Documentation](https://cloudwiry.mayankkumar.ml/docs) <br>
[Video Demo](https://youtu.be/tcknBteu4s4)

## features
- [X] User authentication and session management
- [X] Implementation of the blob storage server
- [X] CLI interface
- [X] User based access control on who can access the files
- [X] Deployed the application using docker compose on bare metal machine
- [X] File compression using zstandard lib
- [X] User Based Access Control with specific controls for read and update an object
- [X] Support for versioning of each object

### System Architecture
![image](https://user-images.githubusercontent.com/24864829/151631425-eadb289c-28fe-4016-a26c-22e95cf1c381.png)

### Database Design
![image](https://user-images.githubusercontent.com/24864829/151632944-cce5f605-beef-4487-a94d-45fcd6a0b6f7.png)
