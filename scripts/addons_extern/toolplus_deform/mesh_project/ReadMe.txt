Install:


1. Put the map with this file in it in blenders addon folder.

2. Go to the Add-on section in the user preference tab.

3. Enable the addon named Mesh: Projection Operators (in the Mesh add-on section)

4. Not there? Use Refresh (bottom of user preference), restart blender or Google how to insall add-ons.









Operator: Project Mesh onto UV Surface

	Projects selected mesh object(s) onto the surface of the active mesh,
 using the active UV map for guidance.
	
	

How to:
	
	

-Select the meshes and apply any modifiers that should be included. 
	
-Make sure the target is the active mesh and the correct uv map selected.
	
-Align the camera so that the origin of the projection objects is projected onto the surface.
	
-Call the function "".
	
	

Usecase:
	The purpose is to project a mesh onto the surface of another mesh. 
	
The function viewed equally to applying texture to the surface,
	but instead of a texture it uses a mesh with a 3D component.
	
Initial purpose was to project "flat" meshes onto a surface, 
but it works with any mesh that you want to fit to the surface.
	
	

[Settings]
	

Axis Aligned: 
	The mesh will be fit to the surface using the axis closest aligned with camera direction. 
	
If disabled the camera direction will be used to determine the direction pointing up/down to the surface.
	
	

Smooth:
	Smooths the projection onto the surface. 
On rough edges it will try to bend the object around the edge.
	
	

Move/Scale/Rotate:
	Rotates the projection