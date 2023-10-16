# Prototype for Cloning Booth tech art installation

This is a prototype service for a future art installation where participants go into a "Cloning Booth".

In the booth, their picture is taken, and they are made to talk about themselves for ~60 seconds. When they exit the booth, they will be able to interact with their virtual clone, streamed through a projector on a wall. 

The idea is by seeing how easy it is to create a virtual clone of someone, it will raise awareness of data privacy and trustworthiness on the internet. 

## To run this
0. This was created using WSL2 for windows. An alias for VLC exe location is needed. As are subscriptions for elevenlabs, d-id and aws s3. 
1. Drop input voice recording and photo into the specified input folder locally
2. Call make_video_e2e to create and play video on VLC

## Todo's
- Tighter security. There is a moment during creation where my public aws s3 bucket has contents
- There is currently no streaming or interactivity with the virtual clones
- Error handling from service calls 
- Proper logging 