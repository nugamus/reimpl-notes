# X3D / H3D engine API surface (extracted from the two EXEs)

Auto-generated from the PE import tables. This is the *complete contract* between

the game executable and the engine DLLs — every engine feature the game can use

is one of these symbols.


## x3d.dll  (87 imported symbols)

- `X3d_Animation_Release`  _(both)_
- `X3d_Camera_Get_Polar`  _(both)_
- `X3d_Camera_Get_Position`  _(both)_
- `X3d_Camera_Release`  _(MissionD only)_
- `X3d_Camera_Set_Fov`  _(both)_
- `X3d_Camera_Set_Polar`  _(both)_
- `X3d_Camera_Set_Position`  _(both)_
- `X3d_Camera_Set_Target`  _(MissionD only)_
- `X3d_Camera_Set_Type`  _(both)_
- `X3d_Convert_From_Polar`  _(both)_
- `X3d_Convert_To_Polar`  _(both)_
- `X3d_Face_Get_Collision_Normal`  _(both)_
- `X3d_Get_Last_Error`  _(both)_
- `X3d_Init_Kernel`  _(both)_
- `X3d_Init_Mathlib`  _(both)_
- `X3d_Init_Ptr`  _(both)_
- `X3d_Init_Vtbl`  _(both)_
- `X3d_Light_Include_Scene_All_Object`  _(MissionD only)_
- `X3d_Light_Set_Color`  _(MissionD only)_
- `X3d_Light_Set_Global_Position`  _(both)_
- `X3d_Light_Set_Multiplier`  _(MissionD only)_
- `X3d_Light_Set_Name`  _(MissionD only)_
- `X3d_Line_Face_Collision`  _(both)_
- `X3d_Load_Sdk_a3d`  _(both)_
- `X3d_Load_Sdk_c3d`  _(both)_
- `X3d_Load_Sdk_l3d`  _(both)_
- `X3d_Load_Sdk_o3d`  _(both)_
- `X3d_Load_Sdk_s3d`  _(both)_
- `X3d_Make_Rotation_Matrice_Z`  _(both)_
- `X3d_Map_Create`  _(both)_
- `X3d_Map_Init`  _(both)_
- `X3d_Material_Update`  _(both)_
- `X3d_Matrice_Copy`  _(both)_
- `X3d_Matrice_Init`  _(both)_
- `X3d_Matrice_Mult`  _(both)_
- `X3d_Object_Add_Lod`  _(both)_
- `X3d_Object_Animate_Spline`  _(both)_
- `X3d_Object_Animate_Transition`  _(both)_
- `X3d_Object_Check_Line_Collision`  _(both)_
- `X3d_Object_Check_Sphere_Collision`  _(both)_
- `X3d_Object_Find_First_Face`  _(both)_
- `X3d_Object_Find_Next_Face`  _(both)_
- `X3d_Object_Get_Global_Matrice`  _(both)_
- `X3d_Object_Get_Global_Position`  _(both)_
- `X3d_Object_Get_Local_Matrice`  _(both)_
- `X3d_Object_Get_Local_Position`  _(both)_
- `X3d_Object_Hide`  _(both)_
- `X3d_Object_Release`  _(both)_
- `X3d_Object_Set_Camera_Type`  _(both)_
- `X3d_Object_Set_Global_Position`  _(both)_
- `X3d_Object_Set_Local_Matrice`  _(both)_
- `X3d_Object_Set_Local_Position`  _(both)_
- `X3d_Object_Set_Render_State`  _(both)_
- `X3d_Object_Unhide`  _(both)_
- `X3d_Print`  _(both)_
- `X3d_Release_Kernel`  _(both)_
- `X3d_Render`  _(both)_
- `X3d_Scene_Add_Map`  _(both)_
- `X3d_Scene_All_Light_Include_Object`  _(both)_
- `X3d_Scene_All_Light_Include_Scene_All_Object`  _(both)_
- `X3d_Scene_Create`  _(both)_
- `X3d_Scene_Create_Camera`  _(both)_
- `X3d_Scene_Create_Light`  _(MissionD only)_
- `X3d_Scene_Create_Spot_Light`  _(MissionD only)_
- `X3d_Scene_Find_First_Animation`  _(MissionD only)_
- `X3d_Scene_Find_First_Camera`  _(both)_
- `X3d_Scene_Find_First_Light`  _(both)_
- `X3d_Scene_Find_First_Material`  _(both)_
- `X3d_Scene_Find_First_Object`  _(both)_
- `X3d_Scene_Find_Next_Animation`  _(MissionD only)_
- `X3d_Scene_Find_Next_Light`  _(both)_
- `X3d_Scene_Find_Next_Material`  _(both)_
- `X3d_Scene_Find_Next_Object`  _(both)_
- `X3d_Scene_Get_Animation`  _(both)_
- `X3d_Scene_Get_Object`  _(both)_
- `X3d_Scene_Init_Render`  _(both)_
- `X3d_Scene_Init_Resolution`  _(both)_
- `X3d_Scene_Pick_Object`  _(both)_
- `X3d_Scene_Release`  _(both)_
- `X3d_Scene_Set_Active_Camera`  _(both)_
- `X3d_Scene_Set_Ambient_Light`  _(both)_
- `X3d_Sphere_Create`  _(both)_
- `X3d_Sphere_Face_Collision`  _(both)_
- `X3d_Sphere_Release`  _(both)_
- `X3d_Sphere_Set_Position`  _(both)_
- `X3d_Sphere_Set_Radius`  _(both)_
- `X3d_Vecteur_Normalise`  _(both)_

## h3d.dll  (7 imported symbols)

- `H3d_D3DDriver_Set_Render_State`  _(both)_
- `H3d_Destroy`  _(both)_
- `H3d_Init_Io`  _(both)_
- `H3d_Lock_BackBuffer`  _(both)_
- `H3d_Show_BackBuffer`  _(both)_
- `H3d_Unlock_BackBuffer`  _(both)_
- `H3d_WindowProc`  _(both)_

## 4xvideo.dll  (1 imported symbols)

- `Video4x_Init`  _(both)_

## aviplay.dll  (5 imported symbols)

- `ordinal_1`  _(both)_
- `ordinal_2`  _(both)_
- `ordinal_3`  _(both)_
- `ordinal_4`  _(both)_
- `ordinal_5`  _(both)_
