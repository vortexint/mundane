function rpc --description 'Recursively print file contents in a formatted manner'
    set dir (pwd)  # Default to current directory
    if test (count $argv) -gt 0
        set dir $argv[1]
    end

    set -l tmpfile (mktemp)

    # find and process files
    find $dir -type d \( -name '.*' -prune \) -o -type f -print | while read -l file
        # Check if the file contains human-readable text
        if file --mime-type "$file" | grep -q 'text'
            set -l relative_path (string replace -- "$dir/" "" $file)
            set -l extension (string split -r . $file | tail -n1)

            echo "$relative_path:" >> $tmpfile
            echo '```'"$extension" >> $tmpfile
            cat "$file" >> $tmpfile
            echo >> $tmpfile  # Add a newline
            echo '```' >> $tmpfile
            echo >> $tmpfile  # Add another newline
        end
    end

    # copy contents to clipboard and clean up
    wl-copy < $tmpfile
    rm $tmpfile
end
