# rashell, a **r**elational **a**lgebra **shell**

rashell is a **R**elational **A**lgebra **Shell**. It provides a domain-specific language (DSL) to define and populate relational models and a read–eval–print loop (REPL) interface to query relational models using relational algebra operations. This tool is intended for educational use only, to illustrate in a more interactive way the underlying concepts of relational databases

## Quick Screencast (Duration 02:27)
[![asciicast](https://asciinema.org/a/VScdkwtX0gJSeBIjxNvDYds6y.svg)](https://asciinema.org/a/VScdkwtX0gJSeBIjxNvDYds6y)
## Installation

rashell can be installed via ```pip```:

```shell
$ pip install rashell
```

## Getting started
rashell can be executed by running the ```rashell``` command from a terminal. You will be taken to a REPL interface that allows you define, populate and query relational models:

```shell
$ rashell
Welcome to rashell, an interactive relational algebra shell
Author: Salim Kebir <s.kebir@esti-annaba.dz>
GitHub: https://github.com/skebir/rashell
>>> 
```

You can issue the ```.exit``` command to exit rashell.

## Defining a relational model
> By default multiline mode is enabled in order to be able to define several relationships at the same time. Multiline mode can be disabled/enabled by pressing the <kbd>F3</kbd> key. To execute an instruction in multiline mode, you must use the <kbd>alt + enter</kbd> combination. Otherwise, simply use <kbd>enter</kbd> if multiline mode is disabled.

You can define a relational model as illustrated in the following example:

```shell
>>> Movie(_Code, Title, Genre, Year, #DirectorID) 
      DirectorID references Director.ID
    Director(_ID, Name, Nationality)
>>> 
```
The syntax for defining a relational model is, as you can see, self-describing:
- A relation is defined by specifying its name followed by a parenthesis and then the list of attributes separated by a comma.
- The attributes that form the primary key must be preceded by the symbol ```_```
- Foreign key attributes must be preceded by the ```#``` symbol and the attribute they reference must be specified just after the definition of the Relation.

## Inserting/Deleting tuples
> It may be better to disable the multiline mode (<kbd>F3</kbd> key) from here because each of the following instructions are single-lined.
> 
Once you have defined your relational model, you can populate it using the ```insert``` command as follows:

```shell
>>> Director.insert(1, 'Robert Zemeckis', 'US')
>>> Director.insert(2, 'Stanley Kubrick', 'US')
>>> Director.insert(3, 'David Lynch', 'US')
>>> Director.insert(4, 'Luc besson', 'FR')
>>> Movie.insert(0120663, 'Eyes wide shut' , 'Drame' , 1999, 2)
>>> Movie.insert(0116922, 'Lost Highway' , 'Thriller', 1997, 3)
>>> Movie.insert(0110413, 'Leon' , 'Crime' , 1994, 4)
>>> Movie.insert(2872732, 'Lucy' , 'Action' , 2014, 4)
>>> Movie.insert(0119116, 'The Fifth Element', 'Action' , 1997, 4)
>>> Movie.insert(0166924, 'Mullholland Drive' , 'Thriller', 2001, 3)
>>> Movie.insert(0062622, "2001: A Space Odyssey", 'Adventure', 1968, 2) 
>>> Movie.insert(0081505, 'The shining' , 'Horror' , 1980, 2)
>>> Movie.insert(0109830, 'Forrest Gump' , 'Drame' , 1994, 1)
>>> Movie.insert(0118884, 'Contact' , 'Drame' , 1997, 1)
>>> Movie.insert(0066921, 'A Clockwork Orange' , 'Crime' , 1971, 2)
>>> Movie.insert(0093058, 'Full Metal Jacket' , 'War' , 1987, 2)
>>> Movie.insert(0090756, 'Blue Velvet' , 'Mystery' , 1986, 3)
>>> Movie.insert(0088763, 'Back to the future', 'Adventure', 1985, 1)
>>> 
```

> At this stage of development, rashell only supports three data types: integers, strings and floats. It is unlikely that other data types will be supported in the future as this tool is purely educational.

The ```insert``` command can fail in four cases:
- If the relation does not exist ;
- If the number of issued values is different from the number of attributes of the relation ;
- If the primary key constraint fail ;
- If the foreign key constraint fail. In this case, we can force the insertion by using the ```force_insert``` instruction instead as illustrated in the following example:

```shell
 >>> Movie.insert(0111161, 'The Shawshank Redemption', 'Drama', 1994, 5)
Line 1: Foreign Key constraint failed 5
>>> Movie.force_insert(0111161, 'The Shawshank Redemption', 'Drama', 1994, 5)
>>>
 ```

To delete tuples, you can use the ```delete``` command with a condition as the only parameter as illustrated below:

```shell
>>> Movie.delete(Year < 2000)
>>> Movie
 ──────────────────────────────────────────────────────────── 
   Code           Title          Genre     Year   DirectorID  
 ──────────────────────────────────────────────────────────── 
  2872732         Lucy           Action    2014       4       
  166924    Mullholland Drive   Thriller   2001       3       
 ──────────────────────────────────────────────────────────── 
>>>
```

Like ```insert```, the ```delete``` command can fail because of foreign key constraints. To force deletion, the ```force_delete``` command can be used as shown below:

```shell
>>> Director.delete(Nationality = 'FR')
Line 1: Foreign Key constraint failed {4}
>>> Director.force_delete(Nationality = 'FR')
>>> Director
 ──────────────────────────────────── 
  Id        Name         Nationality  
 ──────────────────────────────────── 
  1    Robert Zemeckis       US       
  3      David Lynch         US       
  2    Stanley Kubrick       US       
 ──────────────────────────────────── 
>>>
```

## Displaying relations and relational model
You can check that the relations you have populated actually contain the tuples you have added by entering the name of the relation followed by the <kbd>enter</kbd> key (or <kbd>alt + enter</kbd> if you have not disabled multiline mode) as illustrated below:

```shell
>>> Director
 ──────────────────────────────────── 
  Id        Name         Nationality  
 ──────────────────────────────────── 
  4      Luc besson          FR       
  3      David Lynch         US       
  1    Robert Zemeckis       US       
  2    Stanley Kubrick       US       
 ──────────────────────────────────── 
>>> Movie
 ───────────────────────────────────────────────────────────────── 
   Code             Title             Genre     Year   DirectorID  
 ───────────────────────────────────────────────────────────────── 
  118884           Contact            Drama     1997       1       
   90756         Blue Velvet         Mystery    1986       3       
   81505         The shining         Horror     1980       2       
  110413            Leon              Crime     1994       4       
  116922        Lost Highway        Thriller    1997       3       
   66921     A Clockwork Orange       Crime     1971       2       
   93058      Full Metal Jacket        War      1987       2       
  109830        Forrest Gump          Drama     1994       1       
  2872732           Lucy             Action     2014       4       
  120663       Eyes wide shut         Drama     1999       2       
  166924      Mullholland Drive     Thriller    2001       3       
   62622    2001: A Space Odyssey   Adventure   1968       2       
  119116      The Fifth Element      Action     1997       4       
 ───────────────────────────────────────────────────────────────── 
>>>
```

You can also display the specification of your relational model to see what relations exist by running the command ```.model```. Moreover, it is possible to display the relational model in its raw form (i.e. that can be copied and pasted as a command in rashell) by using the command ```.raw_model``` as illustrated in the following example:

```shell
>>> .model
╭──────────────────────────────────────────────╮
│ Director(Id, Name, Nationality)              │
│ Movie(Code, Title, Genre, Year, #DirectorID) │
│     DirectorID references Director.Id        │
╰──────────────────────────────────────────────╯
>>> .raw_model
Director(_Id, Name, Nationality)
Movie(_Code, Title, Genre, Year, #DirectorID)
    DirectorID references Director.Id
>>>
```

## Querying the relational model
At this stage, it is now possible to query your relational model using standard relational algebra operations (projection, restriction, join, union, intersection, difference and cartesian product). The table below shows the symbol, meaning and syntax of each of the relational algebra operations supported by rashell:

| Operation | Meaning           | Syntax/Example                                 |
|:---------:|-------------------|------------------------------------------------|
| ``` π ``` | Projection        | ``` π Name, Nationality (Director) ```         |
| ``` σ ``` | Restriction       | ``` σ Year > 2015 (Movie) ```                  |
| ``` ⋈ ``` | Join              | ``` Movie ⋈ Director &#124; DirectorID = ID``` |
| ``` U ``` | Union             | ``` HorrorMovies U ComedyMovies ```            |
| ``` ∩ ``` | Intersection      | ``` HorrorMovies ∩ ComedyMovies ```            |
| ``` - ``` | Difference        | ``` LynchMovies - ComedyMovies ```             |
| ``` X ``` | Cartesian Product | ``` Movie X Director ```                       |

> It may be difficult to write some symbols such as ⋈, σ, π, and ∩ using a combination of keys. To remedy this, rashell allows you to quickly insert an operation by pressing the <kbd>tab</kbd> key.

The result of an operation is displayed immediately after its execution as below:

```shell
>>> π Title, Year (Movie)
 ────────────────────────────── 
          Title           Year  
 ────────────────────────────── 
  2001: A Space Odyssey   1968  
   Back to the future     1985  
     Eyes wide shut       1999  
       The shining        1980  
    Mullholland Drive     2001  
         Contact          1997  
          Leon            1994  
      Forrest Gump        1994  
       Blue Velvet        1986  
   A Clockwork Orange     1971  
      Lost Highway        1997  
    Full Metal Jacket     1987  
          Lucy            2014  
    The Fifth Element     1997  
 ────────────────────────────── 
>>>
```

The result can also be assigned to a temporary relation as below:

```shell
>>> R1 = π Title, Year (Movie)
>>>
```
This will create a new temporary relation called ```R1``` which can in turn be displayed and/or queried using the previous relational algebra operations.

## Loading a relational model from a file
It is also possible to open a pre-populated relational model by specifying at the beginning of the file the relational model followed by zero or more insert/relational algebra operations. The following is the content of a file called ```movies.ra``` (which can be found in the ```examples``` folder of this repository) :

```shell
Movie(_Code, Title, Genre, Year, #DirectorID)
  DirectorID references Director.Id
Director(_Id, Name, Nationality)

Movie.force_insert(0120663, 'Eyes wide shut' , 'Drama' , 1999, 2)
Movie.force_insert(0116922, 'Lost Highway' , 'Thriller', 1997, 3)
Movie.force_insert(0110413, 'Leon' , 'Crime' , 1994, 4)
Movie.force_insert(2872732, 'Lucy' , 'Action' , 2014, 4)
Movie.force_insert(0119116, 'The Fifth Element', 'Action' , 1997, 4)
Movie.force_insert(0166924, 'Mullholland Drive' , 'Thriller', 2001, 3)
Movie.force_insert(0062622, "2001: A Space Odyssey", 'Adventure', 1968, 2) 
Movie.force_insert(0081505, 'The shining' , 'Horror' , 1980, 2)
Movie.force_insert(0109830, 'Forrest Gump' , 'Drama' , 1994, 1)
Movie.force_insert(0118884, 'Contact' , 'Drama' , 1997, 1)
Movie.force_insert(0066921, 'A Clockwork Orange' , 'Crime' , 1971, 2)
Movie.force_insert(0093058, 'Full Metal Jacket' , 'War' , 1987, 2)
Movie.force_insert(0090756, 'Blue Velvet' , 'Mystery' , 1986, 3)
Movie.force_insert(0088763, 'Back to the future', 'Adventure', 1985, 1)

Director.insert(1, 'Robert Zemeckis', 'US')
Director.insert(2, 'Stanley Kubrick', 'US')
Director.insert(3, 'David Lynch', 'US')
Director.insert(4, 'Luc besson', 'FR')
```

To open a file, you just have to specify its name when running rashell. If the file contains no syntactic or semantic errors, the relational model will be displayed immediately as illustrated below:

```shell
$ rashell examples/movies.ra 
Welcome to rashell, an interactive relational algebra shell
Author: Salim Kebir <s.kebir@esti-annaba.dz>
GitHub: https://github.com/skebir/rashell
╭──────────────────────────────────────────────╮
│ Movie(Code, Title, Genre, Year, #DirectorID) │
│     DirectorID references Director.Id        │
│ Director(Id, Name, Nationality)              │
╰──────────────────────────────────────────────╯
>>>
```


## Keyboard Shortcuts
- <kbd>F3</kbd> Toggle multiline mode
- <kbd>tab</kbd> Insert operation
- <kbd>enter</kbd> Run command when multiline mode is enabled
- <kbd>control + l</kbd> Clear screen
- <kbd>control + d</kbd> Exit rashell

## Acknowledgments
We would like to thank the contributors of the following packages without whom rashell would not have been possible:
- **Python Prompt Toolkit** : https://github.com/prompt-toolkit/python-prompt-toolkit
- **textX** : https://github.com/textX/textX
- **Rich** : https://github.com/Textualize/rich