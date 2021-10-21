import ast
import _ast
from .types import List


def getvar(self, name: str):
    return self.variables.get(
        f'{self.namespace}.{name}',
        self.variables.get(
            f'{self.namespace[:self.namespace.rfind(".")]}.{name}',
            self.variables.get(
                f'main.{name}', {}
            )
        )
    )
