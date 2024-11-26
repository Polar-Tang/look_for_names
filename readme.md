### Usage
You ony need to update this variable
![alt text](image.png)
Which is the SFSESSID
![alt text](image-1.png)
And then run it:
```sh   
nice -n 10 python3 main.py
```
Notice the nice comand at the start, it's to avoid lot's of consuming, like 100% of CPU consume

##### Keywords (variable)
The keywords variable will be the word used to search for the files, if you put two words greyhat will look for a file that match the two words. So these keywords will define the pdf results.
![alt text](image-2.png)
##### PDF keywords (variable)
Instead of that, This variable will define what the script will search in the PDFs.
![alt text](image-3.png)
In this example we search for the terms "cross boarder" and the results will contain that in the file name, so "look_for_name" will inspect all of these results recursively for the pdf_keywords which is "mercado libre" and trace