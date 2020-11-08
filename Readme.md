# golly-maps

Code for turning Game of Life patterns into Golly maps (ListLife arrays).

How to use golly-maps as a submodule:

From the repo of interest, add the golly-maps repo as a submodule named "gollymaps"
(no dash to make it simpler to import):

```
cd my-repo
git submodule add git@github.com:golly-splorts/golly-maps.git gollymaps
git submodule update --init
```

Now you will be able to import the gollymaps submodule from Python and start using it:

```
from gollymaps import maps

s1, s2 = maps.twocolor_randommap(100,100)
print(s1)
print(s2)
```

