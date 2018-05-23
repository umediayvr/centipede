import qbs
import qbs.File
import qbs.TextFile
import qbs.FileInfo
import "installExtra/mainGroup.qbs" as MainGroup

Project {
  id: main
  property string name: "ingestor"
  property string releaseType
  property int pythonMajorVersion

  Probe {
    id: info
    property string fileName: "info.json"
    property var data
    configure: {
      // making sure the info file exists
      if (!File.exists(fileName)){
        throw new Error("Cannot find: " + fileName)
      }

      // parsing info contents
      data = JSON.parse(new TextFile(fileName).readAll())
      return data
    }
  }

  Application {
    name: "defaultPython3"
    MainGroup {
      name: main.name
      version: info.data.version
      pythonMajorVersion: 3
      releaseType: main.releaseType

      condition: (main.pythonMajorVersion === undefined || main.pythonMajorVersion == pythonMajorVersion)
    }
  }

  Application {
    name: "defaultPython2"
    MainGroup {
      name: main.name
      version: info.data.version
      pythonMajorVersion: 2
      releaseType: main.releaseType

      condition: (main.pythonMajorVersion === undefined || main.pythonMajorVersion == pythonMajorVersion)
    }
  }
}
