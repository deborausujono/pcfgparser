To run the test using the default setup:
```python test_cfg.py```

This will use the rules from `data/weighted.rule` and the raw test data from `data/tst.raw`, and output the resulting parse trees to `data/tst.parse`. In the case where the parser fails to parse a sentence, it will output a formatted string that will be skipped by EVALB, the bracket scoring system used to evaluate the parser. An example of output parse trees using our test data set can be found in `data/tst.parse`. Additionally, running the test will also output a set of randomly generated sentences using our grammar. An example of these randomly generated sentences can be found in `data/random.raw`.

Our pre-extracted rules (`data/weighted.rule`) were trained using a subset of Penn Treebank data, modified to support binary branching. To extract rules using your own training data, run:
```python train_cfg.py training_file```

This will save the weighted and unweighted rules in `data/weighted.rule` and `data/unweighted.rule` respectively by default. You can modify this behavior by changing the constants in `train_cfg.py` file. Your training data has to use the same bracketing format as our training data (`data/trn.parse`), but the newlines do not matter. Also note that the parser only supports binary branching, except for unary rules for terminal nodes.

To use the parser:
```
from cfg import *
parser = PCFGParser()
sent = “The title is very bad”
tree = parser.parse(sent.split())
```

The example above will create a parser instance using `data/weighted.rule` grammar file. You can alternatively create a parser instance using your own grammar file:
```parser = PCFGParser(grammar_file)```

The grammar_file has to follow the format of our grammar file: One line per rule, space separated (e.g. `S NP VP -0.00549451931764` for S => NP VP).

Implementation Details
----------------------
This parser handles unseen words by assigning <UNK> tag to words only occurring once during training. The weight for a rule containing <UNK> is obtained using <UNK> count, and this weight is used to calculate probabilities involving unseen words during test.

The parser also deletes non-terminal rules that only occur once in the training data to avoid assigning a probability of 1.0 to rare-occurring production rules.

None will be returned if the parser fails to parse a sentence.

Evaluation
----------
Recall: 70.88  
Precision: 84.71  
FMeasure: 77.18

The parser was evaluated using EVALB. A more detailed summary can be found in eval.txt.