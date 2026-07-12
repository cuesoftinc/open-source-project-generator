package filesystem

import (
	"fmt"
	"os"
	"path/filepath"
)

func CreateProjectStructure(projectPath string, folders []string) error {
	if _, err := os.Stat(projectPath); err == nil {
		if err := os.RemoveAll(projectPath); err != nil {
			return fmt.Errorf("failed to remove existing project directory: %w", err)
		}
	}

	for _, folder := range folders {
		folderPath := filepath.Join(projectPath, folder)
		if err := os.MkdirAll(folderPath, 0750); err != nil {
			return fmt.Errorf("failed to create folder %s: %w", folder, err)
		}
	}

	return nil
}
