<h1 align="center">ID SUIT</h1>
<p align="center">Application to perform operations on Idents given to the particulars in DMC</p>

<p align="center">
    <img src="images\is_ui_1.png" alt="FORMAT">
</p>
<p align="center">
    <img src="images\is_ui_2.png" alt="REPLACE">
</p>
<p align="center">
    <img src="images\is_ui_3.png" alt="COMPUTE">
</p>

## Installation

1. Double click "Id_Suit_Setup.exe".
2. Enter the password in "Password: " label.
3. The installation folder will be defaultly set to local user program folder, but user can change the path if needed.
4. after setting installation path, click on "Next".
5. Check in the "Create a desktop shortcut" if needed.
6. Click "Next" and then "Install" to install the application.

## Getting Started

### Prerequisites

#### catalog

> To support each sub applications of ID SUIT, the "catalog" directory should be present in the local drive "C:" directly.

## Usage and description

### Usage

1. The application includes 3 main functions namely,
   i.   Formatting the idents
   ii.  Replaceing the idents
   iii.  Computing the idents
2. Authors can use the processes as per their convenience in authoring process.
3. The application only supports to edit ATA specific DMCs. No generic modules will be edited including local or common repositories.

### Description

1. Formatting:

   - Modifies the idents as per brex requirement.
   - User can choose the type of particular for which idents to be modified.
   - contains 3 subfunctions.
     1. Continue - Modifies the selected ids as per brex requirement.
     2. Clear - Clears the input box.
     3. Quit - Terminates the action in at the instance.
2. Replacing:

   - Replaces the ids as per the input given by "id_replacenment_template.xlsx".
   - User can choose the type of ID to be replaced.
   - Allowed ID types for replacement:
     1. Warnings - Replces warning ids in "OLD" column of the template to ids in "NEW" column.
     2. Cautions - Replces caution ids in "OLD" column of the template to ids in "NEW" column.
     3. Consumables - Replces supply ids in "OLD" column of the template to ids in "NEW" column.
     4. Tools - Replces tool ids in "OLD" column of the template to ids in "NEW" column.
     5. Other - Replces ids under of mentioned attribute under mentioned element as per "OLD" and "NEW" columns in the template.
   - Input formats allowed for "Other" ID types:
     1. "Element_Name Attribute_Name": Replaces the IDs mentioned in the "OLD" column of the template to IDs in "NEW" column if the ID is present as the attribute value of "Attribute_Name" within "Element_Name".
     2. "* Attribute_Name": Replaces the IDs of "OLD" to "NEW" if the ID is present as the attribute value of "Attribute_Name" within any element.
     3. "* *": Replaces the IDs of "OLD" to "NEW" if the ID is present as the attribute value of any attribute within any element.
   - Contains 4 subfunctions:
     1. Download: Downloads the "id_replacement_template.xlsx" to the path given for input.
     2. Quit: Terminates the ongoing action.
     3. Clear: Clears the input given.
     4. OK: Replaces the idents of selected types.
3. Computing:

   - Computing or compiling the ids will add the idents and details given in the "id_compilation_template.xlsx" to the corresponding repository.
   - Also user can select the type of idents to be created and added to the repository.
   - Contains 5 subfunctions:
     1. Download: Downloads "id_compilation_template.xlsx" to the given input path.
     2. Quit: Terminates the ongoing action.
     3. Clear: Clears the input given.
     4. Remove Idents: Removes the ids given in template from the repository.
     5. Add Idents: Adds the ids given in the template to the repository.

> NOTE:
>
> 1. Keep a backup copy of the working folder before performing any atomization process.
> 2. The application is only compatible for S1000D 4-1 issue.
> 3. Please fill the data only within the template downloaded from the application.

### Summary

#### Description of functions

| Function | Description                                                                        |
| -------- | ---------------------------------------------------------------------------------- |
| FORMAT   | Formats the idents as per brex requirement.                                        |
| REPLACE  | Replaces the given ids in "OLD" column of the template to ids in the "NEW" column. |
| COMPUTE  | Adds the idents and details given in the template to corresponding repository      |

#### ID formats according to BREX

| ID                | Format                                   |
| ----------------- | ---------------------------------------- |
| Figure            | fig-[0-9]{4}                             |
| Graphic           | fig-[0-9]{4}-gra[0-9]{4}                 |
| Hotspot           | fig-[0-9]{4}-gra[0-9]{4}-AUTOID_[0-9]{3} |
| RFU               | rfu-[0-9]{3}                             |
| Table             | tab-[0-9]{4}                             |
| Multimedia        | mmo-[0-9]{4}                             |
| Levelled Para     | par-[0-9]{4}                             |
| Para              | para-[0-9]{4}                            |
| Procedural Step   | stp-[0-9]{4}                             |
| Supply            | sup-[0-9]{4,5}                           |
| Support Equipment | seq-[0-9]{4,5}                           |
| Spare             | spa-[0-9]{4}                             |

#### Pattern input for "Other" type ID replacement

| Input Format                | Example                 | Description                                                      |
| --------------------------- | ----------------------- | ---------------------------------------------------------------- |
| Element_Name Attribute_Name | graphic infoEntityIdent | Replaces OLD to NEW in infoEntityIdent within graphic element.   |
| * Attribute_Name            | * InfoEntityIdent       | Replaces infoEntityIdent present in any element from OLD to NEW. |
| * *                         | * *                     | Replacces OLD to NEW present in any attribute under any element. |
