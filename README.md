# ABBA Eval

This repo showcases a simple (and silly?) LLM eval:

> Can the LLM generate a four line poem that follows the ABBA rhyme scheme?

## Background

The ABBA rhyme scheme is a four-line poem where the first and last lines rhyme, and the second and third lines rhyme. 
For example:

```
In the realm of code and collaboration, (A)
Where developers unite and innovation thrives, (B)
GitHub stands tall, a platform that survives, (B)
Fostering creativity and inspiration. (A)
```

## The Challenge

Can you use LLMs to generate ABBA poems? If so, how?
Out of the box today only Claude 3 Opus somewhat reliably generates ABBA poems.
But there are prompting tricks you can apply to make smaller models generate ABBA poems as well.

## Repo

Notebooks:

1. Lets you generate the poems in various ways
2. Lets you label the results
3. Lets you compare the results

Package only contains the labeling code from PigeonXT, had to copy it in to make a minor change to the printing of the results.

## Contributing

If you'd like to contribute, for example by adding more:

1. Models
2. Evaluation Criteria
3. Prompting Strategies

Feel free to create an issue so we can discuss it!