import io
import re
import os
import sys
import shutil
import tokenize

"""
Python Script Formatter
"""
class Formatter:

    """ Parse/Format Script """
    def parse(self, file=None):
        if not file or not os.path.isfile(file):
            return False
        self.file = file

        # Next statement and indent level
        self.find_stmt = 1
        self.level = 0

        # Open the file
        self.fr = io.open(file)

        # Raw file lines.
        self.raw = self.fr.readlines()
        
        # Rstrip and expand line tabs
        self.lines = []
        for line in self.raw:
            self.lines.append(self._rstrip(line).expandtabs() + "\n")
        self.lines.insert(0, None)
        self.index = 1
        
        # List if line number and indent pairs
        self.stats = []

        # Save the newlines from the file
        self.newlines = self.fr.newlines

        # Format the file
        self._run()

        # Write out and close the file
        self._write()
        return True

    """ RStrip Line 
    
    Strip a line of trailing whitespaces, tabs, etc.
    """
    def _rstrip(self, line, JUNK='\n \t'):
        i = len(line)
        while i > 0 and line[i-1] in JUNK:
            i -= 1
        return line[:i]

    """ Get Leading Space
    
    Get the number of leading whitespace characters.
    """
    def _getlspace(self, line):
        i, n = 0, len(line)
        while i < n and line[i] == " ":
            i += 1
        return i

    """ Run Formatter 
    
    Begin processing and formatting the Python script.
    """
    def _run(self):
        tokenize.tokenize(self._getline, self._tokeneater)
        # Remove trailing empty lines.
        lines = self.lines
        while lines and lines[-1] == "\n":
            lines.pop()
        # Sentinel.
        stats = self.stats
        stats.append((len(lines), 0))
        # Map count of leading spaces to # we want.
        have2want = {}
        # Program after transformation.
        after = self.after = []
        # Copy over initial empty lines -- there's nothing to do until
        # we see a line with *something* on it.
        i = stats[0][0]
        after.extend(lines[1:i])
        for i in range(len(stats)-1):
            thisstmt, thislevel = stats[i]
            nextstmt = stats[i+1][0]
            have = self._getlspace(lines[thisstmt])
            want = thislevel * 4
            if want < 0:
                # A comment line.
                if have:
                    # An indented comment line.  If we saw the same
                    # indentation before, reuse what it most recently
                    # mapped to.
                    want = have2want.get(have, -1)
                    if want < 0:
                        # Then it probably belongs to the next real stmt.
                        for j in xrange(i+1, len(stats)-1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                if have == self._getlspace(lines[jline]):
                                    want = jlevel * 4
                                break
                    if want < 0:           # Maybe it's a hanging
                                           # comment like this one,
                        # in which case we should shift it like its base
                        # line got shifted.
                        for j in xrange(i-1, -1, -1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                want = have + self._getlspace(after[jline-1]) - \
                                       self._getlspace(lines[jline])
                                break
                    if want < 0:
                        # Still no luck -- leave it alone.
                        want = have
                else:
                    want = 0
            assert want >= 0
            have2want[have] = want
            diff = want - have
            if diff == 0 or have == 0:
                after.extend(lines[thisstmt:nextstmt])
            else:
                for line in lines[thisstmt:nextstmt]:
                    if diff > 0:
                        if line == "\n":
                            after.append(line)
                        else:
                            after.append(" " * diff + line)
                    else:
                        remove = min(self._getlspace(line), -diff)
                        after.append(line[remove:])
        return self.raw != self.after

    """ Write Formatted File
    
    Close the file handle used for reading the lines, open the file for writing,
    then dump the formatted new lines array.
    """
    def _write(self):
        self.fr.close()
        
        # Strip out any empty lines
        self.final = []
        for line in self.after:
            if not re.match(r'^\s*$', line):
                self.final.append(line)
        
        # Write the contents to the file
        self.fw = io.open(self.file, 'w')
        self.fw.writelines(self.final)
        self.fw.close()

    """ Get Line
    
    Get a line used for tokenization.
    """
    def _getline(self):
        if self.index >= len(self.lines):
            line = ""
        else:
            line = self.lines[self.index]
            self.index += 1
        return line

    """ Line Eater
    
    Consume a line for tokenization.
    """
    def _tokeneater(self, type, token, (sline, scol), end, line,
                   INDENT=tokenize.INDENT,
                   DEDENT=tokenize.DEDENT,
                   NEWLINE=tokenize.NEWLINE,
                   COMMENT=tokenize.COMMENT,
                   NL=tokenize.NL):

        if type == NEWLINE:
            # A program statement, or ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            self.find_stmt = 1

        elif type == INDENT:
            self.find_stmt = 1
            self.level += 1

        elif type == DEDENT:
            self.find_stmt = 1
            self.level -= 1

        elif type == COMMENT:
            if self.find_stmt:
                self.stats.append((sline, -1))
                # but we're still looking for a new stmt, so leave
                # find_stmt alone

        elif type == NL:
            pass

        elif self.find_stmt:
            # This is the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, or an
            # ENDMARKER.
            self.find_stmt = 0
            if line:   # not endmarker
                self.stats.append((sline, self.level))