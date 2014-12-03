task :default => [:test]

task :test do
    sh "python -m unittest discover tests \"Test*.py\""
end

task :doc do
    sh "doxygen docs/config"
end
