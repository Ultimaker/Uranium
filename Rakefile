task :test do
    FileList['tests/*/Test*.py'].each do |file|
        sh "PYTHONPATH=. python #{file}"
    end
end

task :benchmark do
    FileList['tests/benchmarks/*/profile*.py'].each do |file|
        sh "PYTHONPATH=. kernprof -l -v #{file}"
    end
end

task :doc do
    sh "doxygen docs/config"
end
