# PartAnimatorulator
PartAnimatorulator is a tool for editing Need for Speed Underground 2's PARTS_ANIMATIONS.BIN files. It's based on AJ_Lethal's and RedCarDriver's research.

# What you can do with this tool:
1. Easily rename Animation slots (With automatic padding, and find&replace function)
2. Change pivot positions
3. Change car xname (with automatic hashing).
4. Edit animation frames (with interpolation for easier usage).

I'd recommend to use LANCEREVO8's animation's file as base for your car mods, since it has longest name and padding.

# Q/A
Q: Can I edit angles of animations with this tool?

A: Yes. With latest update you can edit angles of animations. Just open the Animations file, open the slot you want, set first and last frames, click Tools>Interpolate Animslot and done.


Q: There was supposed to be Copy and Delete buttons for AnimSlots. Why they were removed?

A: Previously I thought that simply deleting/copying an anim slot will work, but it turned out that it causes game to crash. Again, to implement it properly it needs more research on how part_animations files work.


# Credits
Vasya (me) - making this tool

AJ_Lethal and RedCarDriver - Reverse Engineering

NFS2019, Darknes, RKBDI - Beta Testing
