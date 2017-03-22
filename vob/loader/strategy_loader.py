#coding:utf-8
import codecs
import sys
import traceback

from six import exec_
from .base_strategy_loader import AbsStrategyLoader

class FileStrategyLoader(AbsStrategyLoader):

    def load(self, strategy, scope):
        with codecs.open(strategy, encoding='utf-8') as f:
            source_code = f.read()
        return self.compile_strategy(source_code, strategy, scope)

    def compile_strategy(self, source_code, strategy, scope):
        try:
            code = compile(source_code, strategy, 'exec')
            exec_(code, scope)
            return scope
        except Exception as e:
            traceback.print_exc()

"""
Testing code
"""
def main():
    fsl = FileStrategyLoader()
    source = fsl.load('test.py', {}) 
    source['test_print']()
    source['test_pd']()

if __name__ == '__main__':
    main()
