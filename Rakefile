task :test do
    sh "python -m unittest discover tests \"Test*.py\""
end

task :benchmark do
    FileList['tests/benchmarks/*/profile*.py'].each do |file|
        sh "PYTHONPATH=. kernprof -l -v #{file}"
    end
end

task :doc do
    sh "doxygen docs/config"
end
