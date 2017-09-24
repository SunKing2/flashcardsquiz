

orig = r'''
# $rc = AskHardest() - ask the currently hardest-rated question
#   returns
#     0 if question was asked successfully
#     1 if no question could be found
#     2 if user has requested end of quiz
sub AskHardest() {
    my $rating = $#gQByRating;
    while ($rating >= 0) {
        next unless length($gQByRating[$rating]);
        for my $q (split(/ /, $gQByRating[$rating])) {
            next unless $prompt'qord - $gWhenAsked[$q] >= $config'mri;
            my $result = AskQ $q;
            if ($result == 0) { return 0; } # asked
            if ($result == 1) { return 2; } # EOF
            # if ($result == 2) { continue; } # did not match pattern
        }
    }
    continue { $rating--; }
    1;
}

# $rc = AskOldest() - ask the currently oldest question
#   returns
#     0 if question was asked successfully
#     1 if no question could be found
#     2 if user has requested end of quiz
sub AskOldest() {
    for my $q (@gQByAge) {
        next unless $prompt'qord - $gWhenAsked[$q] >= $config'mri;
        my $result = AskQ $q;
        if ($result == 0) { return 0; } # asked
        if ($result == 1) { return 2; } # EOF
        # if ($result == 2) { continue; } # did not match pattern
    }
    1;
}

# $result = AskQ($qNumber) - ask a question
#
# returns 0 if question was asked
# returns 1 if user signalled end of file
# returns 2 if question did not match filter and could not be asked

sub AskQ ($) {
    my ($q) = @_;
    die "Oops ($q >= $gQCount)\nAborting" if $q >= $gQCount;
    my ($answer, $flags, $question);
    {
        my $qIndex = $q * $k'fields;
        $flags        = $gQData[$qIndex+$k'fFlags];
        $answer       = $gQData[$qIndex+$k'fAnswer];
        $answer       = lc $answer if $flags =~ /C/;
        $question     = $gQData[$qIndex+$k'fQuestion];
        return 2
          unless &$config::question_filter($question)
          && &$config::answer_filter($answer);
        $prompt'note  = $gNotes =~ /^\Q$question\E\t(.*)/m ? $1 : '';
        $prompt'note  =
          length($prompt'note)
          ? "$prompt'note\n$gQData[$qIndex+$k'fNote]"
          : $gQData[$qIndex+$k'fNote];
        $prompt'note =~ s/^\n//;
        $prompt'note =~ s/<br>|<p>/\n/g;
        $prompt'text  = sprintf("[%d] %s: ", ++$prompt'qord, $question);
    }

    my $time = 0;

    $gWhenAsked[$q] = $prompt'qord;

    if ($flags =~ /O/) { # don't care about order
        my (%answer, %found);
        my $count = 0;
        for my $word (split(/\s+/, $answer)) { $answer{$word} = 1; $count++; }
        my $originalCount = $count;
        my $isFirstQ = 1;
        while ($count > 0) {
            unless ($isFirstQ) {
                print %found
                  ? "Enter another answer, or press return to see them all.\n"
                  : "Press return to see the correct answer, or try again.\n";
            }
            my $read = (ReadLine $time, ($flags =~ /C/));
            defined $read ? chop $read : return 1;
            $isFirstQ = 0;
            ($read =~ /\S/) || return GiveUp $q;
            for my $word (split(/\s+/, $read)) {
                $answer{$word}
                  ? $found{$word}++
                      ? print("You have already entered `$word'.\n")
                      : $count--
                  : print("`$word' is not correct.\n");
            }
        }
    }
    else { # not in unordered mode
        my $read = ReadLine $time, ($flags =~ /C/);
        defined $read ? chop $read : return 1;
        $read eq $answer || return GiveUp $q;
    }
    GotIt $q, $time;
}

# $rc = AskRandom() - ask a question at random, weighting for difficulty
#   returns
#     0 if question was asked successfully
#     1 if the selected question's timer hasn't yet expired
#     2 if user has requested end of quiz
sub AskRandom() {
    for my $i (1..20) {
        my $rand = rand($gTotalRating);
        my $q = 0;
        my $width = $gQCount2;
        while ($width > 1) {
            $width >>= 1;
            my $mid = $q + $width;
            if ($mid <= $gQCount && $rand >= $gRatingTree[$mid-1]) {
                $rand -= $gRatingTree[$mid-1];
                $q = $mid;
            }
        }
        if ($prompt'qord - $gWhenAsked[$q] >= $config'mri) {
            my $result = AskQ $q;
            if ($result == 0) { return 0; } # asked
            if ($result == 1) { return 2; } # EOF
            # if ($result == 2) { continue; } # did not match pattern
        }
    }
    1;
}

# $rc = AskReview() - ask a review question, from the recent errors list
#   returns
#     0 if question was asked successfully
#     1 if the selected question's timer hasn't yet expired, or if no errors
#     2 if user has requested end of quiz
sub AskReview() {
    ($#gErrors>=0 && $prompt'qord-$gWhenAsked[$gErrors[0]] >= $config'mri)
      ? ( (AskQ shift @gErrors) ? 2 : 0 )
      : 1;
}

# DoAddQuestion(@ARGV)
# process '-a question answer flags note file.qz'
#   by adding a question to a file, creating file if necessary
sub DoAddQuestion(@) {
    my @argv = @_;
    my @fields;
    $fields[$k'fQuestion] = shift @argv;
    $fields[$k'fAnswer] = shift @argv;
    $fields[$k'fRating] = '+' . ($config'max_rating+1);
    $fields[$k'fAge] = 0;
    $fields[$k'fFlags] = shift @argv;
    $fields[$k'fNote] = shift @argv;

    LoadData @argv;

    {
        my $qIndex = $k'fQuestion;

        # look to see if question already exists
        while ($qIndex <= $#gQData) {
            last if $fields[$k'fQuestion] eq $gQData[$qIndex];
            $qIndex += $k'fields;
        }

        # up the question count if question is new
        $gFileNum_QuestionCount[0]++ if $qIndex > $#gQData;

        # store new fields in global array
        $qIndex -= $k'fQuestion;
        @gQData[$qIndex..$qIndex+$k'fields-1] = @fields;
    } # my $qIndex

    # mark question file as dirty
    TouchQ 0;

    SaveData;
} # DoAddQuestion

# DoAddQuestions(@ARGV)
# process '-A [input-file] file.qz'
#   by adding questions from the input file
#   (each lines looks like: question tab answer tab flags tab note)
sub DoAddQuestions(@) {
    my @argv = @_;
    my $inputFile = $#argv > 0 ? shift @argv : '-';

    my (@fields);

    # constant fields
    $fields[$k'fRating] = '+' . ($config'max_rating+1);
    $fields[$k'fAge] = 0;

    LoadData @argv;

    EOpenFile *IN, "<$inputFile";
    while (<IN>) {
        chop;
        @_ = split(/\t/);
        die "Wrong number of fields in this line:\n$_\nAborting"
          unless $#_ == $k'fields - 1;
        $fields[$k'fQuestion] = $_[0];
        $fields[$k'fAnswer] = $_[1];
        $fields[$k'fFlags] = $_[2];
        $fields[$k'fNote] = $_[3];
        {
            my $qIndex = $k'fQuestion;
            while ($qIndex <= $#gQData) {
                last if $_[0] eq $gQData[$qIndex];
                $qIndex += $k'fields;
            }
            $gFileNum_QuestionCount[0]++ if $qIndex > $#gQData;
            $qIndex -= $k'fQuestion;
            @gQData[$qIndex..$qIndex+$k'fields-1] = @fields;
        }
    }
    close(IN);

    # mark question file as dirty
    TouchQ 0;

    SaveData;
} # DoAddQuestions

# DoDeleteQuestion(@ARGV)
# process '-d question file.qz'
#   by deleting a question from a file
sub DoDeleteQuestion(@) {
    my @argv = @_;
    my $question = shift @argv;

    LoadData @argv;

    {
        my $qIndex = $k'fQuestion;
        while ($qIndex <= $#gQData) {
            last if $question eq $gQData[$qIndex];
            $qIndex += $k'fields;
        }
        die "No such question: '$question'\n" unless $qIndex <= $#gQData;
        $gFileNum_QuestionCount[0]--;

        # delete data
        splice(@gQData, $qIndex-$k'fQuestion, $k'fields);
    }

    # mark question file as dirty
    TouchQ 0;

    SaveData;
} # DoDeleteQuestion

# DoListQuestions(@ARGV)
# process '-l file.qz...'
#   by listing all questions in named files
sub DoListQuestions(@) {
    my @argv = @_;
    LoadData @argv;

    # measure field widths
    my @tWidths = (0) x $k'fields;
    {
        my $fieldIndex = 0;
        for my $tField (@gQData) {
            my $length =
              ($fieldIndex == $k'fRating && $tField =~ /^\+/)
              ? 3
              : length($tField);
            $tWidths[$fieldIndex] = $length if $tWidths[$fieldIndex] < $length;
            $fieldIndex = 0 if ++$fieldIndex == $k'fields;
        }
    }

    # build printf format
    my $fmt =
        '%'
      . $tWidths[$k'fRating] .'s '.'%-'
      . $tWidths[$k'fQuestion] .'.'
      . $tWidths[$k'fQuestion] . 's '.'%-'
      . $tWidths[$k'fAnswer] .'.'
      . $tWidths[$k'fAnswer] . 's ';
    my $indent = ' ' x ($tWidths[$k'fRating] + $tWidths[$k'fQuestion] + 13);

    for my $q (
        sort{
            $gQData[$k'fRating+$k'fields*$b]
              <=> $gQData[$k'fRating+$k'fields*$a]
              || $gQData[$k'fAge+$k'fields*$b] <=> $gQData[$k'fAge+$k'fields*$a]
        }0..$gQCount-1
      )
    {
        my $qIndex = $q * $k'fields;
        if ($gQData[$_ = $qIndex + $k'fAge]) {
            my @data = localtime($gQData[$_]);
            printf "%04d-%02d-%02d ", $data[5]+1900, $data[4]+1, $data[3];
        }
        else { print "-not-seen- "; }
        printf $fmt,
          (FormatRating $gQData[$qIndex + $k'fRating]),
          $gQData[$qIndex + $k'fQuestion],
          $gQData[$qIndex + $k'fAnswer];
        print "\n";
        $_ = $gQData[$qIndex + $k'fNote];
        print "$indent$_\n" if length($_);
    }

} # DoListQuestions

# DoListStats - list file stats
sub DoListStats () {
    my $solved = 0;
    my $totalRating = 0;
    my $unseen = 0;
    my $unsolved = 0;
    my $age_sum = 0;
    my $now = time;
    my $count = 0;

    # calculate stats
    {
        my $qIndex = $k'fRating;
        my $offsetq = $k'fQuestion - $k'fRating;
        my $offseta = $k'fAnswer - $k'fRating;
        my $offsetage = $k'fAge - $k'fRating;
        while ($qIndex <= $#gQData) {
            next
              unless &$config::question_filter($gQData[$qIndex + $offsetq])
              && &$config::answer_filter($gQData[$qIndex + $offseta]);
            $age_sum += $gQData[$qIndex+$offsetage];
            $count++;
            my $rating = $gQData[$qIndex];
            if ($rating =~ /^\+/) { $unseen++; }
            elsif ($rating == $config'max_rating) { $unsolved++; }
            else { $solved++; $totalRating += $rating; }
        }
        continue { $qIndex += $k'fields; }
    }

    # print report
    my $seen = $solved + $unsolved;
    printf "Total: %d\n", $unseen+$seen;
    printf "Unseen: %d (%d%%)\n", $unseen, 0.5+100*($unseen/($seen+$unseen))
      if $unseen;
    print  "Solved: $solved";
    printf " (%d%%)", 0.5+100*$solved/$seen if $seen;
    print  "\nUnsolved: $unsolved";
    printf " (%d%%)", 0.5+100*$unsolved/$seen if $seen;
    print  "\n";
    printf "Mean solution time: %.1f s\n", $totalRating/$solved if $solved;
    printf "Mean difficulty: %.1f s\n",
      (100*($unsolved+$unseen)+$totalRating)/($seen+$unseen)
      if $unsolved || $unseen;
    print "Mean solution age: ",FormatTime(int($now - $age_sum/$count)), "\n"
      if $count;
    my $t = 0;
    {
        my $i = 0;
        my $offsetq = $k'fQuestion - $k'fAge;
        my $offseta = $k'fAnswer - $k'fAge;
        while ($i <= $#gQByAge) {
            my $qIndex = $gQByAge[$i++]*$k'fields + $k'fAge;
            next
              unless &$config::question_filter($gQData[$qIndex + $offsetq])
              && &$config::answer_filter($gQData[$qIndex + $offseta]);
            $t = $gQData[$qIndex];
            last;
        }
    }
    print "Oldest solution: ", ($t ? FormatTime($now-$t) : 'never'), "\n";
} # DoListStats

# DoRunQuiz(@ARGV)
# process 'qz file.qz...'
#   by running a quiz
sub DoRunQuiz(@) {
    my @argv = @_;
    $SIG{'TSTP'} = \&HandleTSTP if $gEnvironment eq 'unix';
    $gSessionStart = time;

    # load external notes if necessary
    if (defined $config'notes) {
        EOpenFile(*NOTES, '<'.$config'notes);
        local($/) = undef;
        $gNotes = <NOTES>;
        close(NOTES);
    }

    # load data
    @argv = <*.qz> if $#argv == -1;
    LoadData @argv;
    if ($gQCount <= 0) {
        print "There are no questions in the files you specified.\n";
        exit 0;
    }
    MungeData;
    if (time - $gSessionStart > 2){
        print "Press return to begin.\n";
        $_ = <STDIN>;
    }

    # normalise algorithm distribution
    my @algProbs = split(/;/, $config'programs{$config'program}, 4);
    {
        my $tS = 0;
        for my $t (@algProbs) { $tS += $t; }
        for my $t (@algProbs) { $t /= $tS; }
    }

    $gQCorrect = 0;
    $prompt'qord = 0;

    $gTotalTime = 0;
    my $tries = 0;
    $gSessionStart = time;
  ask:while (1) {

        # pick an algorithm
        my $algorithm = 0;
        {
            my $t = rand;
            while ($t>0) { $t -= $algProbs[$algorithm++]; }
            $algorithm--;
        }

        # ask the question
        my $rc =
          &{(\&AskHardest,\&AskOldest,\&AskRandom,\&AskReview)[$algorithm]};
        if ($rc == 1) {
            if ($algorithm <=1 ) {
                print "No more questions available.\n";
                last ask;
            }
            else { $tries++; next ask; }
        }
        elsif ($rc == 2) { last ask; }
        $tries = 0;
    }
    continue {
        if ($tries >= 20){
            print "Giving up after $tries tries at picking a question.\n";
            last;
        }
    }

    SaveData;
    $prompt'qord--;
    &S;
}

# EOpenFile(*HANDLE, "<filename) - open file or die trying
sub EOpenFile(*$) {
    local(*HANDLE) = shift @_;
    my $file = shift @_;
    open(HANDLE, $file) || die "open(HANDLE, \"$file\") failed: $!\n";
}

# $string = FormatTime($interval) - format a positive time interval for display
sub FormatTime ($) {
    my $interval = shift;
    if ($interval < 60) { return "$interval s"; }
    $interval = int($interval/60);
    if ($interval < 60) { return "$interval m"; }
    $interval = int($interval/60);
    if ($interval < 24) { return "$interval h"; }
    $interval = int($interval/24);
    "$interval d";
}

# $string = FormatRating($rating) - format either 'new' or numeric
sub FormatRating ($) { my($r) = @_; $r =~ s/^\+.*/new/; $r; }

# 0 = GiveUp($qNumber) - record that user gave up on this question
sub GiveUp ($) {
    my($q) = @_;
    print "$prompt'note\n" if length($prompt'note);
    print "The correct answer is '$gQData[$q*$k'fields+$k'fAnswer]'". "  ("
      . (FormatRating $gQData[$q*$k'fields+$k'fRating])
      . "-$config'max_rating)\n";
    push(@gErrors, $q);
    SetRating $q, $config'max_rating;
    $prompt'lastq = $q;
    0;
}

# 0 = GotIt($qNumber, $time) - record that user correctly answered question
sub GotIt ($$) {
    my($q, $time) = @_;
    my $oldAge;
    {
        my $qIndex = $q * $k'fields + $k'fAge;
        $oldAge = $gQData[$qIndex];
        $gQData[$qIndex] = time;
    }

    {
        my $oldRating = $gQData[$k'fields*$q+$k'fRating];
        my $newRating =
          int($oldRating =~ /^\+/? $time : (1+2*$oldRating+$time)/3);
        $gTotalTime += $time;
        $newRating < 1 ? ($newRating = 1) : $newRating > $config'max_rating
          && ($newRating = $config'max_rating);
        print "$prompt'note\n" if length($prompt'note);
        print 'Correct.  ('
          .($oldAge ? (FormatTime time-$oldAge) : 'never'). ':'
          . (FormatRating $oldRating)
          . "-$newRating)\n";
        $gQCorrect++;

        # update question fields
        SetRating $q, $newRating;
    }

    # update chronological list
    {
        my $low = 0;
        my $high = $gQCount;
        while ($high - $low > 1) {
            my $mid = int(($low + $high) / 2);
            my $comp = $gQData[$gQByAge[$mid]*$k'fields+$k'fAge] <=> $oldAge;
            if ($comp < 0) { $low = $mid; }
            elsif ($comp > 0) { $high = $mid; }
            else { $low = $high = $mid; last; }
        }
        while ($gQData[$gQByAge[$low]*$k'fields+$k'fAge] == $oldAge && $low > 0)
        {
            $low--;
        }
        while ($gQData[$gQByAge[$high]*$k'fields+$k'fAge] == $oldAge
            && $high < $gQCount-1)
        {
            $high++;
        }
        {
            my $tQ = $low;
            while ($tQ<=$high) {
                if ($gQByAge[$tQ] == $q){
                    push(@gQByAge, splice(@gQByAge, $tQ, 1));
                    last;
                }
                $tQ++;
            }
        }
    }

    TouchQ $q;
    $prompt'lastq = $q;
    0;
}

# HandleTSTP() - TSTP signal handler
sub HandleTSTP ($) {
    $SIG{'TSTP'} = \&HandleTSTP;
    my $stopped_at = time;
    kill 'STOP', $$;
    if ($prompt'waiting) {
        $prompt'start += time - $stopped_at;
        print $prompt'text;
    }
    $prompt'resumed = 1;
}

sub JoinPath (@) {
    join(
         $gEnvironment eq 'mac' ? ':'
        :$gEnvironment eq 'unix' ? '/'
        :$gEnvironment eq 'dos' ? '\\'
        : die,
        @_
    );
}

# LoadData - load quiz data
sub LoadData (@) {
    my (@files) = @_;

    # first expand directory names (3.0.7)
    {
        my $i;
        for ($i=0; $i<=$#files; $i++) {
            next unless -d $files[$i];
            opendir(DIR, $files[$i])
              || die "$files[$i]: can't read directory: $!\n";
            my @subfiles =
              grep((!/^\.{1,2}$/) && (/\.qz$/||-d (JoinPath $files[$i], $_)),
                readdir(DIR));
            closedir(DIR);
            for my $sf (@subfiles) { $sf = JoinPath $files[$i], $sf; }
            splice(@files, $i, 1, @subfiles);
        } # for ($i=0;...)
    } # my $i

    $gQCount = 0;
    for my $file (@files) {
        my $fileQCount = 0;
        EOpenFile *IN, "<$file";
        while (<IN>) {
            chomp;
            my @fields = split(/\t/, $_, 100);
            if ($#fields == -1) { next; }
            elsif ($#fields == 1) { push(@fields, @config'default_fields_2); }
            die "$file line $.: Can't parse line:\n$_\n"
              . "Expected $k'fields fields, got $#fields+1.\nAborting"
              unless $#fields == $k'fields-1;
            push(@gQData, @fields);
            $gQCount++;
            $fileQCount++;
        } # while (<IN>)
        close(IN);

        push(@gFileNum_Dirty, 0);
        push(@gFileNum_FileName, $file);
        push(@gFileNum_QuestionCount, $fileQCount);
    } # for my $file
}

# MungeData - precalculate information useful for running a quiz
sub MungeData () {

    # round $gQCount up to a power of two
    for ($gQCount2 = 1; $gQCount2 < $gQCount; $gQCount2 <<= 1) { }

    # calculate rating information
    @gQByRating = ('') x ($config'max_rating + 2);

    # ($u0,$s0) = times; # DEBUG
    $gTotalRating = 0;
    {
        my $q = 0;
        my $qIndex = $k'fRating;
        while ($q<$gQCount) { # a fun loop
            my $rating = $gQData[$qIndex];
            $gTotalRating += $gRatingTree[$q] = $rating;
            $gQByRating[$rating] .= "$q ";
            next unless $q % 2;
            my $t1 = $q-1;
            $gRatingTree[$q] += $gRatingTree[$t1];
            my $t2 = 1;
            my $t3 = $q & (1 + $q);

            while (($t1-=$t2) > $t3){
                $t2 += $t2;
                $gRatingTree[$q] += $gRatingTree[$t1];
            }
        }
        continue { $q++; $qIndex += $k'fields; }
    }

    # ($u1,$s1) = times; printf "time: %5.2f %5.2f\n", $u1-$u0, $s1-$s0; # DEBUG

    # build chronological list
    {
        $#gQByAge = $gQCount - 1;
        my $q = $gQCount;
        my $qIndex = $q * $k'fields + $k'fAge;
        while ($q-- > 0) { $gQByAge[$q] = $qIndex -= $k'fields; }
    }

  # perl 5.10.0 segfaults if the following line is in the preceding block.
  # if placed here, it silently fails when returning from MungeData.
  # @gQByAge = sort { $gQData[$a] <=> $gQData[$b] || int(rand(3))-1; } @gQByAge;
  # It works fine if you don't do the sort in place:
    my (@perl510sux) =
      sort { $gQData[$a] <=> $gQData[$b] || int(rand(3))-1; } @gQByAge;
    @gQByAge = @perl510sux;
    for my $q1 (@gQByAge) { $q1 = int($q1/$k'fields); }

    # build last-asked list
    @gWhenAsked = (-$config'mri) x $gQCount;
}

# $answer = ReadLine($time, $makelc) - prompt for a line and
#   update $time, convert to lower case if desired
sub ReadLine ($$) {
    my ($totaltime, $makelc) = @_;
    my $duration;
    my $time = 0;
    local($_);

    $prompt'resumed = 0;
    $prompt'waiting = 1;
    print $prompt'text;
    $prompt'start = time;

    while (1) {
        $_ = <STDIN>;
        $prompt'waiting = 0;
        if ($prompt'resumed) {
            $prompt'resumed = 0;
            next unless defined $_;
        }
        defined $_ || return $_;
        $duration = time - $prompt'start - (length $_)/$config'typing_speed;
        last if $_ eq '';
        if    (s/^;exit//i) { return undef; }
        elsif (s/^;//) { print "(", join(',',eval($_)), ")\n";}
        elsif ($gEnvironment ne 'mac' && s/^!//) { system $_; }
        elsif ((defined $prompt'lastq) && s/^\+//) {
            chop;
            my $note;
            ($note = ($gQData[$prompt'lastq*$k'fields+$k'fNote].=$_))=~
              s/<br>|<p>/\n/g;
            print "The note for the previous question now reads:\n$note\n";
        }
        else { $time += $duration; last; }
        $prompt'start = time;
        $prompt'waiting = 1;
        print $prompt'text;
    }
    $_[0] += $time;
    s/^[ \t]*//;
    s/[ \t]+$//;
    $makelc ? "\L$_" : $_;
}

# typically invoked from CLI as: ;s
sub S () {
    printf "\nYou answered %d question%s correctly of %d",
      $gQCorrect, $gQCorrect == 1 ? '' : 's', $prompt'qord;
    printf " (%.1f%%)", 100 * $gQCorrect/$prompt'qord if $prompt'qord;
    print ".\n";
    printf "You took on average %.1f seconds to answer correctly.\n",
      $gTotalTime/$gQCorrect
      if $gQCorrect;
    print "Congratulations!\n"
      if $prompt'qord && $gQCorrect/$prompt'qord > 0.9;
    my $elapsed = time - $gSessionStart;
    printf "Elapsed time: %d:%02d:%02d\n",
      int($elapsed/3600), int($elapsed/60) % 60, $elapsed % 60;
    print "\nCurrent statistics for this question set:\n";
    DoListStats;
}

# SaveData() - save quiz data
sub SaveData () {
    my $qIndex = 0;
    for my $fileNumber (0..$#gFileNum_Dirty) {
        if ($gFileNum_Dirty[$fileNumber]) {
            my $tName = $gFileNum_FileName[$fileNumber];
            my $tNewName = $tName;

            $tNewName =~ s/\.[^.]*$//;
            $tNewName .= '.new';
            EOpenFile *FILE, ">$tNewName";
            my $tCount = $gFileNum_QuestionCount[$fileNumber];
            my $tFormat = join("\t", ('%s') x $k'fields) . "\n";
            while ($tCount-- > 0) {
                (printf FILE $tFormat,@gQData[$qIndex..$qIndex+$k'fields-1])
                  || die "Error writing to $tNewName ($!)\nAborting";
                $qIndex += $k'fields;
            }
            close(FILE) || die "Error closing $tNewName\nAborting";
            rename($tNewName, $tName)
              || die "Error renaming $tNewName to $tName\nAborting";
            $gFileNum_Dirty[$fileNumber] = 0;
        }
        else {
            $qIndex += $k'fields*$gFileNum_QuestionCount[$fileNumber];
        }
    }
}

# SetRating($qNumber, $newRating) - set question's difficulty rating
sub SetRating ($$) {
    my($qNumber, $newRating) = @_;
    my $qIndex = $k'fields*$qNumber + $k'fRating;
    my $oldRating = $gQData[$qIndex];
    if ($newRating ne $oldRating) {
        $gQByRating[$oldRating] =~ s/\b$qNumber //
          || die "Panic (oldRating=$oldRating;g[]=$gQByRating[$oldRating])";
        $gQByRating[$newRating] .= "$qNumber ";
        $gQData[$qIndex] = $newRating;
        TouchQ $qNumber;

        my $diff = $newRating - $oldRating;
        $gTotalRating += $diff;
        while ($qNumber < $gQCount) { # ELFS: prove that this works
            $gRatingTree[$qNumber] += $diff;
            $qNumber |= $qNumber+1;
        }
    }
}

# TouchQ($qNumber) - mark a question as dirty
sub TouchQ ($) {
    my $qNumber = $_[0];
    my $fileNumber = 0;

    if ($qNumber == 0) { $fileNumber = 1; } # exceptional case: no questions
    else {
        my $q = 0;
        while ($q <= $qNumber) {
            die
              "Internal error: TouchQ($_[0]), fileNumber=$fileNumber\nAborting"
              if $fileNumber > $#gFileNum_QuestionCount;
            $q += $gFileNum_QuestionCount[$fileNumber++];
        }
    }
    $gFileNum_Dirty[--$fileNumber] = 1;
}
'''

ss = [
    [';\n', '\n'],
    ['config::', 'config.'],
    ["config'", 'config.'],
    ['prompt::', 'prompt.'],
    ["prompt'", 'prompt.'],
    ["k'", 'k.'],
    ['my $', '$'],
    ['my @', '@'],
    ['$g', 'g.g'],
    ['@g', 'g.g'],
    ['++', '+=1'],
    ['$', ''],
    ['@', ''],
    [' {\n', ':\n'],
    ['{\n', ':\n'],
    [' ():\n', '():\n'],
    ['\n}', '\n'],
    ['\n  }', '\n'],
    ['\n    }', '\n'],
    ['\n      }', '\n'],
    ['\n        }', '\n'],
    ['\n          }', '\n'],
    ['||', 'or'],
    ['&&', 'and'],
    ['\nsub', '\ndef'],
    ['= time', '= Time.time()'],
    ['#gQByRating', 'len(g.gQByRating)'],
    ['next unless length(g.gQByRating[rating])', 'if not len(g.gQByRating[rating]): continue'],
    ['for q (split(/ /, g.gQByRating[rating])):', 'for q in " ".split(g.gQByRating[rating]):'],
    ['next unless prompt.qord - g.gWhenAsked[q] >= config.mri', 'if not prompt.qord - g.gWhenAsked[q] >= config.mri: continue'],
    ['result = AskQ q', 'result = AskQ(q)'],
    ['if (result == 0) { return 0; } # asked', 'if (result == 0): return 0 # asked'],
    ['if (result == 1) { return 2; } # EOF', 'if (result == 1): return 2 # EOF'],
    ['\n    continue { rating--; }', '        rating-=1'],
    ['\n    1', '\n    return 1'],
    ['q (g.gQByAge)', 'q in g.gQByAge'],
    ['''
        # if (result == 2) { continue; } # did not match pattern''', ''],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['def AskQ():\n    my (q) = _', 'def AskQ(q):'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ['aaa', 'bbb'],
    ]

s = orig

for oldnew in ss:
    s = s.replace(oldnew[0], oldnew[1])
    
print (s[:])

if 3 > 2 + 1: c = 2

